import sqlite3
import json
from typing import List, Optional, Dict, Any, Tuple
from .models import *
import logging

logger = logging.getLogger(__name__)

class GameDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """初始化数据库表结构"""
        with self.get_connection() as conn:
            # 玩家表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    tg_id INTEGER PRIMARY KEY,
                    username TEXT,
                    name TEXT DEFAULT '修仙者',
                    level INTEGER DEFAULT 1,
                    exp INTEGER DEFAULT 0,
                    world TEXT DEFAULT '',
                    world_level INTEGER DEFAULT 1,
                    attributes TEXT DEFAULT '{}',
                    spirit_stones TEXT DEFAULT '{}',
                    inventory TEXT DEFAULT '{}',
                    equipment TEXT DEFAULT '{}',
                    sect_id INTEGER,
                    sect_position TEXT DEFAULT '弟子',
                    sect_contribution INTEGER DEFAULT 0,
                    status TEXT DEFAULT '{}',
                    last_signin TEXT,
                    last_hunt TEXT,
                    created_at TEXT
                )
            ''')
            
            # 世界表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS worlds (
                    name TEXT PRIMARY KEY,
                    world_level INTEGER,
                    description TEXT DEFAULT '',
                    spirit_stone_type TEXT DEFAULT '下品灵石',
                    attributes TEXT DEFAULT '{}'
                )
            ''')
            
            # 装备表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS equipment (
                    name TEXT PRIMARY KEY,
                    slot TEXT,
                    quality TEXT DEFAULT '普通',
                    level_requirement INTEGER DEFAULT 1,
                    world_level_requirement INTEGER DEFAULT 1,
                    description TEXT DEFAULT '',
                    attributes TEXT DEFAULT '{}',
                    special_effects TEXT DEFAULT '{}'
                )
            ''')
            
            # 物品表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS items (
                    name TEXT PRIMARY KEY,
                    item_type TEXT DEFAULT '消耗品',
                    description TEXT DEFAULT '',
                    effects TEXT DEFAULT '{}',
                    usable INTEGER DEFAULT 1
                )
            ''')
            
            # 宗门表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    leader_id INTEGER,
                    description TEXT DEFAULT '',
                    level INTEGER DEFAULT 1,
                    exp INTEGER DEFAULT 0,
                    max_members INTEGER DEFAULT 50,
                    buffs TEXT DEFAULT '{}',
                    defense_value INTEGER DEFAULT 0,
                    created_at TEXT
                )
            ''')
            
            # 宗门贡献表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sect_contributions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sect_id INTEGER,
                    player_id INTEGER,
                    artifact_name TEXT,
                    contribution_value INTEGER,
                    contributed_at TEXT,
                    FOREIGN KEY (sect_id) REFERENCES sects (id),
                    FOREIGN KEY (player_id) REFERENCES players (tg_id)
                )
            ''')
            
            # 战斗表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS battles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    battle_type TEXT,
                    challenger_id INTEGER,
                    target_id INTEGER,
                    status TEXT DEFAULT 'pending',
                    result TEXT DEFAULT '{}',
                    created_at TEXT
                )
            ''')
            
            # 商店表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS shops (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    world_name TEXT,
                    item_name TEXT,
                    item_type TEXT DEFAULT 'item',
                    price INTEGER,
                    currency TEXT DEFAULT '下品灵石',
                    stock INTEGER DEFAULT -1
                )
            ''')
            
            # 管理员表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    tg_id INTEGER PRIMARY KEY,
                    username TEXT,
                    created_at TEXT
                )
            ''')
            
            # 游戏配置表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS game_configs (
                    config_key TEXT PRIMARY KEY,
                    config_value TEXT
                )
            ''')
            
            conn.commit()
    
    # 玩家相关方法
    def create_player(self, player: Player) -> bool:
        """创建新玩家"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT INTO players (
                        tg_id, username, name, level, exp, world, world_level,
                        attributes, spirit_stones, inventory, equipment,
                        sect_id, sect_position, sect_contribution, status,
                        last_signin, last_hunt, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    player.tg_id, player.username, player.name, player.level, player.exp,
                    player.world, player.world_level,
                    json.dumps(player.attributes), json.dumps(player.spirit_stones),
                    json.dumps(player.inventory), json.dumps(player.equipment),
                    player.sect_id, player.sect_position, player.sect_contribution,
                    json.dumps(player.status), player.last_signin, player.last_hunt,
                    player.created_at
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"创建玩家失败: {e}")
            return False
    
    def get_player(self, tg_id: int) -> Optional[Player]:
        """获取玩家信息"""
        try:
            with self.get_connection() as conn:
                row = conn.execute(
                    'SELECT * FROM players WHERE tg_id = ?', (tg_id,)
                ).fetchone()
                
                if row:
                    return Player(
                        tg_id=row['tg_id'],
                        username=row['username'] or "",
                        name=row['name'],
                        level=row['level'],
                        exp=row['exp'],
                        world=row['world'],
                        world_level=row['world_level'],
                        attributes=json.loads(row['attributes'] or '{}'),
                        spirit_stones=json.loads(row['spirit_stones'] or '{}'),
                        inventory=json.loads(row['inventory'] or '{}'),
                        equipment=json.loads(row['equipment'] or '{}'),
                        sect_id=row['sect_id'],
                        sect_position=row['sect_position'],
                        sect_contribution=row['sect_contribution'],
                        status=json.loads(row['status'] or '{}'),
                        last_signin=row['last_signin'],
                        last_hunt=row['last_hunt'],
                        created_at=row['created_at']
                    )
        except Exception as e:
            logger.error(f"获取玩家信息失败: {e}")
        return None
    
    def update_player(self, player: Player) -> bool:
        """更新玩家信息"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    UPDATE players SET 
                        username=?, name=?, level=?, exp=?, world=?, world_level=?,
                        attributes=?, spirit_stones=?, inventory=?, equipment=?,
                        sect_id=?, sect_position=?, sect_contribution=?, status=?,
                        last_signin=?, last_hunt=?
                    WHERE tg_id=?
                ''', (
                    player.username, player.name, player.level, player.exp,
                    player.world, player.world_level,
                    json.dumps(player.attributes), json.dumps(player.spirit_stones),
                    json.dumps(player.inventory), json.dumps(player.equipment),
                    player.sect_id, player.sect_position, player.sect_contribution,
                    json.dumps(player.status), player.last_signin, player.last_hunt,
                    player.tg_id
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"更新玩家信息失败: {e}")
            return False
    
    def get_players_by_sect(self, sect_id: int) -> List[Player]:
        """获取宗门成员列表"""
        try:
            with self.get_connection() as conn:
                rows = conn.execute(
                    'SELECT * FROM players WHERE sect_id = ? ORDER BY sect_contribution DESC',
                    (sect_id,)
                ).fetchall()
                
                players = []
                for row in rows:
                    player = Player(
                        tg_id=row['tg_id'],
                        username=row['username'] or "",
                        name=row['name'],
                        level=row['level'],
                        exp=row['exp'],
                        world=row['world'],
                        world_level=row['world_level'],
                        attributes=json.loads(row['attributes'] or '{}'),
                        spirit_stones=json.loads(row['spirit_stones'] or '{}'),
                        inventory=json.loads(row['inventory'] or '{}'),
                        equipment=json.loads(row['equipment'] or '{}'),
                        sect_id=row['sect_id'],
                        sect_position=row['sect_position'],
                        sect_contribution=row['sect_contribution'],
                        status=json.loads(row['status'] or '{}'),
                        last_signin=row['last_signin'],
                        last_hunt=row['last_hunt'],
                        created_at=row['created_at']
                    )
                    players.append(player)
                return players
        except Exception as e:
            logger.error(f"获取宗门成员失败: {e}")
            return []
    
    # 世界相关方法
    def create_world(self, world: World) -> bool:
        """创建世界"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO worlds 
                    (name, world_level, description, spirit_stone_type, attributes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (world.name, world.world_level, world.description,
                     world.spirit_stone_type, json.dumps(world.attributes)))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"创建世界失败: {e}")
            return False
    
    def get_worlds_by_level(self, world_level: int) -> List[World]:
        """获取指定等级的世界列表"""
        try:
            with self.get_connection() as conn:
                rows = conn.execute(
                    'SELECT * FROM worlds WHERE world_level = ? ORDER BY name',
                    (world_level,)
                ).fetchall()
                
                return [World(
                    name=row['name'],
                    world_level=row['world_level'],
                    description=row['description'],
                    spirit_stone_type=row['spirit_stone_type'],
                    attributes=json.loads(row['attributes'] or '{}')
                ) for row in rows]
        except Exception as e:
            logger.error(f"获取世界列表失败: {e}")
            return []
    
    # 装备相关方法
    def create_equipment(self, equipment: Equipment) -> bool:
        """创建装备"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO equipment 
                    (name, slot, quality, level_requirement, world_level_requirement,
                     description, attributes, special_effects)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    equipment.name, equipment.slot, equipment.quality,
                    equipment.level_requirement, equipment.world_level_requirement,
                    equipment.description, json.dumps(equipment.attributes),
                    json.dumps(equipment.special_effects)
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"创建装备失败: {e}")
            return False
    
    def get_equipment(self, name: str) -> Optional[Equipment]:
        """获取装备信息"""
        try:
            with self.get_connection() as conn:
                row = conn.execute(
                    'SELECT * FROM equipment WHERE name = ?', (name,)
                ).fetchone()
                
                if row:
                    return Equipment(
                        name=row['name'],
                        slot=row['slot'],
                        quality=row['quality'],
                        level_requirement=row['level_requirement'],
                        world_level_requirement=row['world_level_requirement'],
                        description=row['description'],
                        attributes=json.loads(row['attributes'] or '{}'),
                        special_effects=json.loads(row['special_effects'] or '{}')
                    )
        except Exception as e:
            logger.error(f"获取装备信息失败: {e}")
        return None
    
    def get_equipment_by_slot(self, slot: str, player_level: int = 1, world_level: int = 1) -> List[Equipment]:
        """获取指定部位的可用装备"""
        try:
            with self.get_connection() as conn:
                rows = conn.execute('''
                    SELECT * FROM equipment 
                    WHERE slot = ? AND level_requirement <= ? AND world_level_requirement <= ?
                    ORDER BY quality, level_requirement DESC
                ''', (slot, player_level, world_level)).fetchall()
                
                return [Equipment(
                    name=row['name'],
                    slot=row['slot'],
                    quality=row['quality'],
                    level_requirement=row['level_requirement'],
                    world_level_requirement=row['world_level_requirement'],
                    description=row['description'],
                    attributes=json.loads(row['attributes'] or '{}'),
                    special_effects=json.loads(row['special_effects'] or '{}')
                ) for row in rows]
        except Exception as e:
            logger.error(f"获取装备列表失败: {e}")
            return []
    
    # 宗门相关方法
    def create_sect(self, sect: Sect) -> bool:
        """创建宗门"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    INSERT INTO sects (name, leader_id, description, level, exp, max_members, buffs, defense_value, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    sect.name, sect.leader_id, sect.description, sect.level, sect.exp,
                    sect.max_members, json.dumps(sect.buffs), sect.defense_value, sect.created_at
                ))
                sect.id = cursor.lastrowid
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"创建宗门失败: {e}")
            return False
    
    def get_sect(self, sect_id: int) -> Optional[Sect]:
        """获取宗门信息"""
        try:
            with self.get_connection() as conn:
                row = conn.execute(
                    'SELECT * FROM sects WHERE id = ?', (sect_id,)
                ).fetchone()
                
                if row:
                    return Sect(
                        id=row['id'],
                        name=row['name'],
                        leader_id=row['leader_id'],
                        description=row['description'],
                        level=row['level'],
                        exp=row['exp'],
                        max_members=row['max_members'],
                        buffs=json.loads(row['buffs'] or '{}'),
                        defense_value=row['defense_value'],
                        created_at=row['created_at']
                    )
        except Exception as e:
            logger.error(f"获取宗门信息失败: {e}")
        return None
    
    def list_sects(self) -> List[Sect]:
        """获取所有宗门列表"""
        try:
            with self.get_connection() as conn:
                rows = conn.execute(
                    'SELECT * FROM sects ORDER BY level DESC, defense_value DESC'
                ).fetchall()
                
                return [Sect(
                    id=row['id'],
                    name=row['name'],
                    leader_id=row['leader_id'],
                    description=row['description'],
                    level=row['level'],
                    exp=row['exp'],
                    max_members=row['max_members'],
                    buffs=json.loads(row['buffs'] or '{}'),
                    defense_value=row['defense_value'],
                    created_at=row['created_at']
                ) for row in rows]
        except Exception as e:
            logger.error(f"获取宗门列表失败: {e}")
            return []
    
    def get_sect_contributions(self, sect_id: int) -> List[SectContribution]:
        """获取宗门贡献列表"""
        try:
            with self.get_connection() as conn:
                rows = conn.execute('''
                    SELECT * FROM sect_contributions 
                    WHERE sect_id = ? 
                    ORDER BY contribution_value DESC
                ''', (sect_id,)).fetchall()
                
                return [SectContribution(
                    id=row['id'],
                    sect_id=row['sect_id'],
                    player_id=row['player_id'],
                    artifact_name=row['artifact_name'],
                    contribution_value=row['contribution_value'],
                    contributed_at=row['contributed_at']
                ) for row in rows]
        except Exception as e:
            logger.error(f"获取宗门贡献失败: {e}")
            return []
    
    def add_sect_contribution(self, contribution: SectContribution) -> bool:
        """添加宗门贡献"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    INSERT INTO sect_contributions 
                    (sect_id, player_id, artifact_name, contribution_value, contributed_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    contribution.sect_id, contribution.player_id,
                    contribution.artifact_name, contribution.contribution_value,
                    contribution.contributed_at
                ))
                contribution.id = cursor.lastrowid
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"添加宗门贡献失败: {e}")
            return False
    
    def remove_sect_contribution(self, contribution_id: int) -> bool:
        """移除宗门贡献"""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    'DELETE FROM sect_contributions WHERE id = ?', (contribution_id,)
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"移除宗门贡献失败: {e}")
            return False
    
    def update_sect_defense(self, sect_id: int) -> bool:
        """更新宗门防御值"""
        try:
            with self.get_connection() as conn:
                # 计算总防御值
                contributions = self.get_sect_contributions(sect_id)
                total_defense = sum(c.contribution_value for c in contributions)
                
                conn.execute(
                    'UPDATE sects SET defense_value = ? WHERE id = ?',
                    (total_defense, sect_id)
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"更新宗门防御失败: {e}")
            return False
    
    # 管理员相关方法
    def add_admin(self, tg_id: int, username: str = "") -> bool:
        """添加管理员"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO admins (tg_id, username, created_at)
                    VALUES (?, ?, ?)
                ''', (tg_id, username, datetime.now().isoformat()))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"添加管理员失败: {e}")
            return False
    
    def is_admin(self, tg_id: int) -> bool:
        """检查是否为管理员"""
        try:
            with self.get_connection() as conn:
                result = conn.execute(
                    'SELECT 1 FROM admins WHERE tg_id = ?', (tg_id,)
                ).fetchone()
                return result is not None
        except Exception as e:
            logger.error(f"检查管理员权限失败: {e}")
            return False