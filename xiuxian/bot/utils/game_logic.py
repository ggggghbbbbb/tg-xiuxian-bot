import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from database.database import GameDatabase
from database.models import Player, Equipment, Item
import config

class GameLogic:
    def __init__(self, db: GameDatabase):
        self.db = db
    
    def calculate_total_attributes(self, player: Player) -> Dict[str, float]:
        """计算玩家总属性(基础+装备)"""
        total_attrs = player.attributes.copy()
        
        # 装备加成
        for slot, equip_name in player.equipment.items():
            if equip_name:
                equipment = self.db.get_equipment(equip_name)
                if equipment:
                    for attr, value in equipment.attributes.items():
                        total_attrs[attr] = total_attrs.get(attr, 0) + value
        
        # 宗门加成
        if player.sect_id:
            sect = self.db.get_sect(player.sect_id)
            if sect:
                for attr, value in sect.buffs.items():
                    total_attrs[attr] = total_attrs.get(attr, 0) + value
        
        return total_attrs
    
    def calculate_combat_power(self, player: Player) -> int:
        """计算战斗力"""
        attrs = self.calculate_total_attributes(player)
        
        # 战斗力 = 攻击力 * 1.5 + 防御力 * 1.2 + 生命值 * 0.8 + 其他属性综合
        power = (
            attrs.get('攻击力', 0) * 1.5 +
            attrs.get('防御力', 0) * 1.2 +
            attrs.get('生命值', 0) * 0.8 +
            attrs.get('速度', 0) * 0.5 +
            attrs.get('法术强度', 0) * 1.0 +
            attrs.get('暴击率', 0) * 10 +
            attrs.get('闪避率', 0) * 8
        )
        
        return int(power)
    
    def can_level_up(self, player: Player) -> bool:
        """检查是否可以升级"""
        required_exp = self.get_required_exp(player.level)
        return player.exp >= required_exp
    
    def get_required_exp(self, level: int) -> int:
        """获取升级所需经验"""
        return level * 100 + (level // 10) * 500
    
    def level_up(self, player: Player) -> bool:
        """升级"""
        if not self.can_level_up(player):
            return False
        
        required_exp = self.get_required_exp(player.level)
        player.exp -= required_exp
        player.level += 1
        
        # 属性增长
        growth = {
            '攻击力': random.randint(5, 15),
            '防御力': random.randint(3, 12),
            '生命值': random.randint(20, 50),
            '法力值': random.randint(10, 30),
            '速度': random.randint(1, 5)
        }
        
        for attr, value in growth.items():
            player.attributes[attr] = player.attributes.get(attr, 0) + value
        
        # 检查是否可以进入更高级世界
        new_world_level = (player.level - 1) // 100 + 1
        if new_world_level > player.world_level:
            player.world_level = new_world_level
        
        return True
    
    def can_equip(self, player: Player, equipment: Equipment) -> Tuple[bool, str]:
        """检查是否可以装备"""
        if player.level < equipment.level_requirement:
            return False, f"需要等级 {equipment.level_requirement}"
        
        if player.world_level < equipment.world_level_requirement:
            return False, f"需要世界等级 {equipment.world_level_requirement}"
        
        return True, ""
    
    def equip_item(self, player: Player, equip_name: str) -> Tuple[bool, str]:
        """装备物品"""
        if equip_name not in player.inventory or player.inventory[equip_name] <= 0:
            return False, "背包中没有此装备"
        
        equipment = self.db.get_equipment(equip_name)
        if not equipment:
            return False, "装备不存在"
        
        can_equip, msg = self.can_equip(player, equipment)
        if not can_equip:
            return False, msg
        
        # 卸下旧装备
        old_equip = player.equipment.get(equipment.slot, "")
        if old_equip:
            player.inventory[old_equip] = player.inventory.get(old_equip, 0) + 1
        
        # 装备新装备
        player.equipment[equipment.slot] = equip_name
        player.inventory[equip_name] -= 1
        if player.inventory[equip_name] <= 0:
            del player.inventory[equip_name]
        
        return True, f"已装备 {equip_name}"
    
    def use_item(self, player: Player, item_name: str) -> Tuple[bool, str]:
        """使用物品"""
        if item_name not in player.inventory or player.inventory[item_name] <= 0:
            return False, "背包中没有此物品"
        
        item = self.db.get_item(item_name)
        if not item or not item.usable:
            return False, "此物品无法使用"
        
        # 应用物品效果
        result_msgs = []
        for effect, value in item.effects.items():
            if effect in config.PLAYER_ATTRIBUTES:
                player.attributes[effect] = player.attributes.get(effect, 0) + value
                result_msgs.append(f"{effect} +{value}")
            elif effect == "经验":
                player.exp += value
                result_msgs.append(f"经验 +{value}")
            elif effect == "升级":
                for _ in range(value):
                    if self.level_up(player):
                        result_msgs.append("升级成功！")
            elif effect in player.spirit_stones:
                player.spirit_stones[effect] = player.spirit_stones.get(effect, 0) + value
                result_msgs.append(f"{effect} +{value}")
        
        # 扣除物品
        player.inventory[item_name] -= 1
        if player.inventory[item_name] <= 0:
            del player.inventory[item_name]
        
        return True, f"使用 {item_name}：" + "，".join(result_msgs)
    
    def calculate_hunt_rewards(self, player: Player, difficulty: str) -> Dict[str, Any]:
        """计算刷怪奖励"""
        config_data = config.HUNT_DIFFICULTIES.get(difficulty, config.HUNT_DIFFICULTIES['简单'])
        
        results = {
            'injured': False,
            'exp_gained': 0,
            'stones_gained': {},
            'equipment_dropped': [],
            'items_dropped': []
        }
        
        # 判断是否受伤
        if random.random() * 100 < config_data['injury_rate']:
            results['injured'] = True
            # 受伤时间：等级越低时间越长
            injury_hours = max(1, 6 - player.level // 20)
            player.status['injured'] = True
            player.status['injured_until'] = (datetime.now() + timedelta(hours=injury_hours)).isoformat()
        
        # 如果没受伤，计算奖励
        if not results['injured']:
            base_exp = player.level * 10
            results['exp_gained'] = int(base_exp * config_data['reward_multiplier'])
            player.exp += results['exp_gained']
            
            # 灵石奖励
            stone_amount = int(player.level * 5 * config_data['reward_multiplier'])
            stone_type = self.get_world_currency(player.world)
            results['stones_gained'][stone_type] = stone_amount
            player.spirit_stones[stone_type] = player.spirit_stones.get(stone_type, 0) + stone_amount
            
            # 装备掉落（低概率）
            if random.random() < 0.1 * config_data['reward_multiplier']:
                dropped_equip = self.generate_random_equipment(player.level, player.world_level)
                if dropped_equip:
                    results['equipment_dropped'].append(dropped_equip)
                    player.inventory[dropped_equip] = player.inventory.get(dropped_equip, 0) + 1
        
        return results
    
    def generate_random_equipment(self, player_level: int, world_level: int) -> Optional[str]:
        """生成随机装备"""
        # 这里应该从数据库中随机选择符合等级的装备
        # 暂时返回None，实际实现需要查询数据库
        return None
    
    def get_world_currency(self, world_name: str) -> str:
        """获取世界主要货币"""
        # 根据世界获取主要货币类型
        return "下品灵石"  # 默认货币
    
    def calculate_retreat_rewards(self, player: Player, hours: int) -> Dict[str, int]:
        """计算闭关奖励"""
        base_stones = player.level * hours * 2
        world_multiplier = player.world_level * 1.5
        
        total_stones = int(base_stones * world_multiplier)
        currency = self.get_world_currency(player.world)
        
        return {currency: total_stones}
    
    def can_signin_today(self, player: Player) -> bool:
        """检查今天是否可以签到"""
        if not player.last_signin:
            return True
        
        last_signin = datetime.fromisoformat(player.last_signin)
        today = datetime.now().date()
        return last_signin.date() < today
    
    def calculate_signin_rewards(self, player: Player) -> Dict[str, int]:
        """计算签到奖励"""
        base_amount = 50 + player.level * 5
        currency = self.get_world_currency(player.world)
        
        return {currency: base_amount}
    
    def perform_battle(self, challenger: Player, target: Player) -> Dict[str, Any]:
        """执行战斗"""
        challenger_power = self.calculate_combat_power(challenger)
        target_power = self.calculate_combat_power(target)
        
        # 简单的战斗计算
        total_power = challenger_power + target_power
        win_rate = challenger_power / total_power if total_power > 0 else 0.5
        
        challenger_wins = random.random() < win_rate
        
        result = {
            'winner_id': challenger.tg_id if challenger_wins else target.tg_id,
            'loser_id': target.tg_id if challenger_wins else challenger.tg_id,
            'challenger_power': challenger_power,
            'target_power': target_power,
            'win_rate': win_rate
        }
        
        # 奖励和惩罚
        if challenger_wins:
            exp_gain = max(10, target.level * 2)
            challenger.exp += exp_gain
            result['exp_gain'] = exp_gain
        
        return result