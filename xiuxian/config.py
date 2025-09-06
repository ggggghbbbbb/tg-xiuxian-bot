import os
from typing import List

# Bot配置
BOT_TOKEN = "8457177707:AAFL_Vtwxw3ukCjZjoVoPlPSIDEuTmKKLAs"

# 数据库配置
DATABASE_PATH = 'game.db'

# 管理员配置
ADMIN_IDS: List[int] = [
    # 在这里添加管理员的Telegram ID
     5390861579,
]

# 分页配置
PAGE_SIZE = 10

# 世界等级配置
WORLD_LEVELS = {
    1: {"min_level": 1, "max_level": 100, "name": "一级世界"},
    2: {"min_level": 101, "max_level": 200, "name": "二级世界"}, 
    3: {"min_level": 201, "max_level": 300, "name": "三级世界"},
    4: {"min_level": 301, "max_level": 400, "name": "四级世界"},
    5: {"min_level": 401, "max_level": 500, "name": "五级世界"}
}

# 装备品质等级
EQUIPMENT_QUALITIES = [
    '破损', '粗糙', '普通', '精良', '稀有', '史诗', '传说', '神话', '太古', '混沌', '鸿蒙'
]

# 装备部位
EQUIPMENT_SLOTS = {
    '头饰': '头部装备',
    '服饰': '身体装备', 
    '腿部': '腿部装备',
    '手部': '手部装备',
    '鞋子': '脚部装备',
    '武器': '武器装备',
    '法器': '法器装备'
}

# 饰品部位
ACCESSORY_SLOTS = {
    '戒指': '戒指饰品',
    '手串': '手串饰品',
    '腰带': '腰带饰品', 
    '挂件': '挂件饰品',
    '项链': '项链饰品',
    '玉牌': '玉牌饰品',
    '香囊': '香囊饰品',
    '称号': '称号饰品',
    '护符': '护符饰品',
    '符篆': '符篆饰品'
}

# 所有装备槽位
ALL_SLOTS = {**EQUIPMENT_SLOTS, **ACCESSORY_SLOTS}

# 玩家属性
PLAYER_ATTRIBUTES = [
    '攻击力', '防御力', '生命值', '法力值', '速度', '暴击率', 
    '闪避率', '命中率', '法术强度', '韧性', '幸运值'
]

# 法器特殊功能
ARTIFACT_FUNCTIONS = {
    '护体': '减少受到的伤害',
    '增益': '提升某项属性',
    '恢复': '恢复生命或法力',
    '暴击': '增加暴击概率',
    '闪避': '增加闪避概率',
    '吸血': '攻击时恢复生命',
    '反弹': '反弹部分伤害',
    '净化': '清除负面状态',
    '加速': '提升行动速度',
    '破甲': '无视部分防御'
}

# 刷怪难度
HUNT_DIFFICULTIES = {
    '简单': {'injury_rate': 10, 'reward_multiplier': 1.0},
    '普通': {'injury_rate': 30, 'reward_multiplier': 1.5},
    '困难': {'injury_rate': 60, 'reward_multiplier': 2.0}
}

# 闭关时间选项(小时)
RETREAT_HOURS = [1, 3, 6, 12, 24, 48]

# 宗门最大人数
MAX_SECT_MEMBERS = 50

# 宗门最大法宝贡献数
MAX_ARTIFACT_CONTRIBUTION = 10