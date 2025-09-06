from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import json
from datetime import datetime

@dataclass
class Player:
    tg_id: int
    username: str = ""
    name: str = "修仙者"  # 角色名
    level: int = 1
    exp: int = 0
    world: str = ""  # 当前世界
    world_level: int = 1  # 世界等级
    
    # 基础属性
    attributes: Dict[str, float] = field(default_factory=lambda: {
        "攻击力": 100, "防御力": 100, "生命值": 1000, "法力值": 500,
        "速度": 100, "暴击率": 5, "闪避率": 5, "命中率": 90,
        "法术强度": 50, "韧性": 10, "幸运值": 1
    })
    
    # 灵石
    spirit_stones: Dict[str, int] = field(default_factory=lambda: {
        "下品灵石": 1000, "中品灵石": 100, "上品灵石": 10, "极品灵石": 1
    })
    
    # 背包物品
    inventory: Dict[str, int] = field(default_factory=dict)
    
    # 装备
    equipment: Dict[str, str] = field(default_factory=dict)
    
    # 宗门相关
    sect_id: Optional[int] = None
    sect_position: str = "弟子"  # 弟子/长老/副宗主/宗主
    sect_contribution: int = 0
    
    # 状态
    status: Dict[str, Any] = field(default_factory=dict)  # 受伤、闭关等状态
    last_signin: Optional[str] = None
    last_hunt: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class World:
    name: str
    world_level: int  # 世界等级 1-5
    description: str = ""
    spirit_stone_type: str = "下品灵石"  # 主要货币类型
    attributes: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Equipment:
    name: str
    slot: str  # 装备部位
    quality: str = "普通"
    level_requirement: int = 1
    world_level_requirement: int = 1
    description: str = ""
    
    # 属性加成
    attributes: Dict[str, float] = field(default_factory=dict)
    
    # 特殊效果(主要用于法器)
    special_effects: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Item:
    name: str
    item_type: str = "消耗品"  # 消耗品/材料/特殊
    description: str = ""
    effects: Dict[str, Any] = field(default_factory=dict)
    usable: bool = True

@dataclass
class Sect:
    id: int
    name: str
    leader_id: Optional[int] = None
    description: str = ""
    level: int = 1
    exp: int = 0
    max_members: int = 50
    
    # 宗门属性加成
    buffs: Dict[str, float] = field(default_factory=dict)
    
    # 护宗大阵防御值
    defense_value: int = 0
    
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class SectContribution:
    id: int
    sect_id: int
    player_id: int
    artifact_name: str
    contribution_value: int
    contributed_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class Battle:
    id: int
    battle_type: str  # pvp/sect_war/sect_attack
    challenger_id: int
    target_id: int
    status: str = "pending"  # pending/accepted/completed/rejected
    result: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())