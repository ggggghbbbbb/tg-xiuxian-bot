from telegram import Update
from telegram.ext import ContextTypes
from database.database import GameDatabase
from database.models import Player, Equipment, Sect
from bot.keyboards.panels import *
from bot.utils.game_logic import GameLogic
from datetime import datetime, timedelta
import config
import json

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理所有回调查询"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    db = GameDatabase(config.DATABASE_PATH)
    player = db.get_player(user_id)
    
    # 如果需要玩家数据但玩家不存在
    if not player and not data.startswith(('admin_', 'back_to_main')):
        await query.edit_message_text("请先使用 /start 创建角色！")
        return
    
    game_logic = GameLogic(db) if player else None
    
    # 主面板相关
    if data == "back_to_main":
        is_admin = db.is_admin(user_id) or user_id in config.ADMIN_IDS
        await query.edit_message_text(
            "🎮 修仙世界主面板\n\n选择你要进行的操作：",
            reply_markup=main_panel_keyboard(is_admin)
        )
    
    elif data == "panel_player":
        await handle_player_panel(query, player, db, game_logic)
    
    elif data == "panel_inventory":
        await handle_inventory_panel(query, player, db)
    
    elif data == "panel_equipment":
        await query.edit_message_text(
            "⚔️ 装备面板\n\n选择要查看的装备部位：",
            reply_markup=equipment_panel_keyboard()
        )
    
    elif data.startswith("equip_"):
        await handle_equipment_slot(query, data, player, db, game_logic)
    
    elif data == "panel_sect":
        await handle_sect_panel(query, player, db)
    
    elif data == "panel_hunt":
        await query.edit_message_text(
            "🗡️ 外出刷怪\n\n选择刷怪难度：",
            reply_markup=hunt_difficulty_keyboard()
        )
    
    elif data.startswith("hunt_"):
        await handle_hunt(query, data, player, db, game_logic)
    
    elif data == "panel_retreat":
        await query.edit_message_text(
            "🧘‍♂️ 闭关修炼\n\n选择闭关时间：",
            reply_markup=retreat_time_keyboard()
        )
    
    elif data.startswith("retreat_"):
        await handle_retreat(query, data, player, db, game_logic)
    
    elif data == "panel_signin":
        await handle_signin(query, player, db, game_logic)
    
    # 管理员面板
    elif data == "admin_panel":
        if db.is_admin(user_id) or user_id in config.ADMIN_IDS:
            await query.edit_message_text(
                "⚙️ 管理员面板\n\n选择管理功能：",
                reply_markup=admin_panel_keyboard()
            )
        else:
            await query.edit_message_text("❌ 权限不足！")

async def handle_player_panel(query, player: Player, db: GameDatabase, game_logic: GameLogic):
    """处理玩家属性面板"""
    total_attrs = game_logic.calculate_total_attributes(player)
    combat_power = game_logic.calculate_combat_power(player)
    
    # 获取世界等级信息
    world_info = config.WORLD_LEVELS.get(player.world_level, {})
    next_world_level = player.world_level + 1
    next_world_info = config.WORLD_LEVELS.get(next_world_level, {})
    
    text = f"👤 **{player.name}** 的属性面板\n\n"
    text += f"📊 等级：{player.level}\n"
    text += f"⚡ 经验：{player.exp}/{game_logic.get_required_exp(player.level)}\n"
    text += f"🌍 当前世界：{player.world or '未选择'}\n"
    text += f"🏆 世界等级：{player.world_level} ({world_info.get('name', '')})\n"
    
    if next_world_info and player.level >= next_world_info['min_level']:
        text += f"🆙 可进入：{next_world_info['name']}\n"
    
    text += f"⚔️ 战斗力：{combat_power}\n\n"
    
    # 宗门信息
    if player.sect_id:
        sect = db.get_sect(player.sect_id)
        if sect:
            text += f"🏛️ 宗门：{sect.name} ({player.sect_position})\n"
            text += f"💰 贡献：{player.sect_contribution}\n\n"
    else:
        text += "🏛️ 宗门：未加入\n\n"
    
    # 属性详情
    text += "💪 **属性详情**\n"
    for attr in config.PLAYER_ATTRIBUTES:
        base_value = player.attributes.get(attr, 0)
        total_value = total_attrs.get(attr, 0)
        bonus = total_value - base_value
        
        if bonus > 0:
            text += f"  {attr}：{base_value}+{bonus} = {total_value}\n"
        else:
            text += f"  {attr}：{total_value}\n"
    
    text += "\n💎 **灵石**\n"
    for currency, amount in player.spirit_stones.items():
        text += f"  {currency}：{amount}\n"
    
    text += "\n⚔️ **当前装备**\n"
    for slot_name in config.ALL_SLOTS.keys():
        equip_name = player.equipment.get(slot_name, "")
        if equip_name:
            equipment = db.get_equipment(equip_name)
            if equipment:
                attrs_text = "，".join([f"{k}+{v}" for k, v in equipment.attributes.items()])
                text += f"  {slot_name}：{equip_name} ({equipment.quality}，{attrs_text})\n"
            else:
                text += f"  {slot_name}：{equip_name}\n"
        else:
            text += f"  {slot_name}：无\n"
    
    await query.edit_message_text(text, reply_markup=back_keyboard())

async def handle_inventory_panel(query, player: Player, db: GameDatabase):
    """处理背包面板"""
    text = f"🎒 {player.name} 的背包\n\n"
    
    if not player.inventory:
        text += "背包空空如也..."
    else:
        items = list(player.inventory.items())[:20]  # 显示前20个物品
        for item_name, count in items:
            item = db.get_item(item_name)
            equipment = db.get_equipment(item_name)
            
            if item:
                text += f"📦 {item_name} x{count} ({item.item_type})\n"
                text += f"    {item.description}\n"
            elif equipment:
                text += f"⚔️ {equipment_name} x{count} ({equipment.quality})\n"
                attrs_text = "，".join([f"{k}+{v}" for k, v in equipment.attributes.items()])
                text += f"    {attrs_text}\n"
            else:
                text += f"❓ {item_name} x{count}\n"
        
        if len(player.inventory) > 20:
            text += f"\n... 还有 {len(player.inventory) - 20} 种物品"
        
        text += "\n\n💡 使用 /use 物品名 来使用物品"
        text += "\n💡 使用 /equip 装备名 来装备物品"
    
    await query.edit_message_text(text, reply_markup=back_keyboard())

async def handle_equipment_slot(query, data: str, player: Player, db: GameDatabase, game_logic: GameLogic):
    """处理装备槽位选择"""
    slot = data.replace("equip_", "")
    
    if slot == "accessories":
        await query.edit_message_text(
            "💎 饰品装备\n\n选择饰品部位：",
            reply_markup=accessories_keyboard()
        )
        return
    
    # 获取该部位的可用装备
    equipment_list = db.get_equipment_by_slot(slot, player.level, player.world_level)
    
    # 过滤玩家背包中拥有的装备
    available_equipment = []
    for equipment in equipment_list:
        if equipment.name in player.inventory and player.inventory[equipment.name] > 0:
            available_equipment.append(equipment)
    
    current_equip = player.equipment.get(slot, "")
    
    text = f"⚔️ {slot}装备\n\n"
    text += f"当前装备：{current_equip or '无'}\n\n"
    
    if available_equipment:
        text += "可装备的物品：\n"
        for i, equipment in enumerate(available_equipment[:10], 1):
            attrs_text = "，".join([f"{k}+{v}" for k, v in equipment.attributes.items()])
            text += f"{i}. {equipment.name} ({equipment.quality})\n"
            text += f"   {attrs_text}\n"
            text += f"   需要等级{equipment.level_requirement}\n\n"
        
        text += "💡 使用 /equip 装备名 来装备"
    else:
        text += "暂无可装备的物品"
    
    await query.edit_message_text(text, reply_markup=back_keyboard("panel_equipment"))

async def handle_sect_panel(query, player: Player, db: GameDatabase):
    """处理宗门面板"""
    is_member = player.sect_id is not None
    is_leader = False
    
    if is_member:
        sect = db.get_sect(player.sect_id)
        is_leader = sect and sect.leader_id == player.tg_id
    
    await query.edit_message_text(
        "🏛️ 宗门系统\n\n选择操作：",
        reply_markup=sect_panel_keyboard(is_member, is_leader)
    )

async def handle_hunt(query, data: str, player: Player, db: GameDatabase, game_logic: GameLogic):
    """处理刷怪"""
    difficulty = data.replace("hunt_", "")
    
    # 检查是否受伤
    if player.status.get('injured', False):
        if 'injured_until' in player.status:
            injured_until = datetime.fromisoformat(player.status['injured_until'])
            if datetime.now() < injured_until:
                remaining = injured_until - datetime.now()
                hours = int(remaining.total_seconds() // 3600)
                minutes = int((remaining.total_seconds() % 3600) // 60)
                await query.edit_message_text(
                    f"❌ 你目前受伤无法刷怪！\n"
                    f"恢复时间：{hours}小时{minutes}分钟",
                    reply_markup=back_keyboard()
                )
                return
            else:
                # 伤势已恢复
                player.status.pop('injured', None)
                player.status.pop('injured_until', None)
    
    # 检查是否在闭关
    if player.status.get('retreating', False):
        await query.edit_message_text(
            "❌ 闭关中无法刷怪！",
            reply_markup=back_keyboard()
        )
        return
    
    # 执行刷怪
    results = game_logic.calculate_hunt_rewards(player, difficulty)
    
    text = f"🗡️ {difficulty}刷怪结果\n\n"
    
    if results['injured']:
        text += "💥 你在战斗中受伤了！\n"
        text += f"🏥 恢复时间：{player.status.get('injured_until', '未知')}\n"
        text += "在此期间无法进行任何活动"
    else:
        text += "🎉 刷怪成功！\n\n"
        text += f"⚡ 获得经验：{results['exp_gained']}\n"
        
        for currency, amount in results['stones_gained'].items():
            text += f"💎 获得{currency}：{amount}\n"
        
        if results['equipment_dropped']:
            text += f"⚔️ 掉落装备：{', '.join(results['equipment_dropped'])}\n"
        
        if results['items_dropped']:
            text += f"📦 掉落物品：{', '.join(results['items_dropped'])}\n"
        
        # 检查升级
        level_ups = 0
        while game_logic.can_level_up(player):
            game_logic.level_up(player)
            level_ups += 1
        
        if level_ups > 0:
            text += f"\n🎉 连续升级 {level_ups} 次！当前等级：{player.level}"
    
    # 更新最后刷怪时间
    player.last_hunt = datetime.now().isoformat()
    db.update_player(player)
    
    await query.edit_message_text(text, reply_markup=back_keyboard())

async def handle_retreat(query, data: str, player: Player, db: GameDatabase, game_logic: GameLogic):
    """处理闭关修炼"""
    hours = int(data.replace("retreat_", ""))
    
    # 检查状态
    if player.status.get('injured', False):
        await query.edit_message_text(
            "❌ 受伤状态无法闭关！",
            reply_markup=back_keyboard()
        )
        return
    
    if player.status.get('retreating', False):
        await query.edit_message_text(
            "❌ 你已经在闭关中！",
            reply_markup=back_keyboard()
        )
        return
    
    # 开始闭关
    retreat_end = datetime.now() + timedelta(hours=hours)
    player.status['retreating'] = True
    player.status['retreat_end'] = retreat_end.isoformat()
    
    # 计算奖励
    rewards = game_logic.calculate_retreat_rewards(player, hours)
    
    # 添加奖励到玩家
    for currency, amount in rewards.items():
        player.spirit_stones[currency] = player.spirit_stones.get(currency, 0) + amount
    
    db.update_player(player)
    
    text = f"🧘‍♂️ 开始闭关修炼\n\n"
    text += f"⏰ 闭关时间：{hours}小时\n"
    text += f"🏁 结束时间：{retreat_end.strftime('%m-%d %H:%M')}\n\n"
    text += "💰 闭关奖励：\n"
    for currency, amount in rewards.items():
        text += f"  {currency}：+{amount}\n"
    text += "\n⚠️ 闭关期间无法进行其他活动"
    
    await query.edit_message_text(text, reply_markup=back_keyboard())

async def handle_signin(query, player: Player, db: GameDatabase, game_logic: GameLogic):
    """处理签到"""
    if not game_logic.can_signin_today(player):
        await query.edit_message_text(
            "❌ 你今天已经签到过了！",
            reply_markup=back_keyboard()
        )
        return
    
    # 计算签到奖励
    rewards = game_logic.calculate_signin_rewards(player)
    
    # 添加奖励
    for currency, amount in rewards.items():
        player.spirit_stones[currency] = player.spirit_stones.get(currency, 0) + amount
    
    player.last_signin = datetime.now().isoformat()
    db.update_player(player)
    
    text = "📅 签到成功！\n\n💰 获得奖励：\n"
    for currency, amount in rewards.items():
        text += f"  {currency}：+{amount}\n"
    
    await query.edit_message_text(text, reply_markup=back_keyboard())