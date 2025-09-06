from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict, Any
import config

def main_panel_keyboard(is_admin: bool = False):
    """主面板键盘"""
    keyboard = [
        [InlineKeyboardButton("👤 人物属性", callback_data="panel_player")],
        [InlineKeyboardButton("🎒 背包", callback_data="panel_inventory")],
        [InlineKeyboardButton("🛒 商店", callback_data="panel_shop")],
        [InlineKeyboardButton("⚔️ 装备", callback_data="panel_equipment")],
        [InlineKeyboardButton("🏛️ 宗门", callback_data="panel_sect")],
        [InlineKeyboardButton("⚡ 修炼突破", callback_data="panel_breakthrough")],
        [InlineKeyboardButton("🧘‍♂️ 闭关修炼", callback_data="panel_retreat")],
        [InlineKeyboardButton("🗡️ 外出刷怪", callback_data="panel_hunt")],
        [InlineKeyboardButton("📅 签到", callback_data="panel_signin")]
    ]
    
    if is_admin:
        keyboard.append([InlineKeyboardButton("⚙️ 管理员", callback_data="admin_panel")])
    
    return InlineKeyboardMarkup(keyboard)

def admin_panel_keyboard():
    """管理员面板键盘"""
    keyboard = [
        [InlineKeyboardButton("🌍 世界管理", callback_data="admin_worlds"),
         InlineKeyboardButton("⚔️ 装备管理", callback_data="admin_equipment")],
        [InlineKeyboardButton("💊 物品管理", callback_data="admin_items"),
         InlineKeyboardButton("🏛️ 宗门管理", callback_data="admin_sects")],
        [InlineKeyboardButton("👥 玩家管理", callback_data="admin_players"),
         InlineKeyboardButton("🛒 商店管理", callback_data="admin_shops")],
        [InlineKeyboardButton("⚙️ 系统配置", callback_data="admin_config"),
         InlineKeyboardButton("📊 数据统计", callback_data="admin_stats")],
        [InlineKeyboardButton("🔙 返回主面板", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def equipment_panel_keyboard():
    """装备面板键盘"""
    keyboard = []
    
    # 基础装备
    basic_slots = [
        ("👑 头饰", "equip_头饰"), ("👕 服饰", "equip_服饰"),
        ("👖 腿部", "equip_腿部"), ("🧤 手部", "equip_手部"),
        ("👟 鞋子", "equip_鞋子"), ("⚔️ 武器", "equip_武器"),
        ("🔮 法器", "equip_法器")
    ]
    
    for i in range(0, len(basic_slots), 2):
        row = [InlineKeyboardButton(name, callback_data=callback) 
               for name, callback in basic_slots[i:i+2]]
        keyboard.append(row)
    
    # 饰品
    keyboard.append([InlineKeyboardButton("💎 饰品", callback_data="equip_accessories")])
    keyboard.append([InlineKeyboardButton("🔙 返回", callback_data="back_to_main")])
    
    return InlineKeyboardMarkup(keyboard)

def accessories_keyboard():
    """饰品键盘"""
    accessories = [
        ("💍 戒指", "equip_戒指"), ("📿 手串", "equip_手串"),
        ("🔗 腰带", "equip_腰带"), ("🎗️ 挂件", "equip_挂件"),
        ("📿 项链", "equip_项链"), ("🏷️ 玉牌", "equip_玉牌"),
        ("👝 香囊", "equip_香囊"), ("🏆 称号", "equip_称号"),
        ("🛡️ 护符", "equip_护符"), ("📜 符篆", "equip_符篆")
    ]
    
    keyboard = []
    for i in range(0, len(accessories), 2):
        row = [InlineKeyboardButton(name, callback_data=callback) 
               for name, callback in accessories[i:i+2]]
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🔙 返回装备", callback_data="panel_equipment")])
    return InlineKeyboardMarkup(keyboard)

def sect_panel_keyboard(is_member: bool = False, is_leader: bool = False):
    """宗门面板键盘"""
    keyboard = []
    
    if not is_member:
        # 未加入宗门
        keyboard.append([InlineKeyboardButton("🔍 查看宗门", callback_data="sect_list")])
        keyboard.append([InlineKeyboardButton("➕ 申请加入", callback_data="sect_apply")])
    else:
        # 已加入宗门
        keyboard.extend([
            [InlineKeyboardButton("ℹ️ 宗门信息", callback_data="sect_info")],
            [InlineKeyboardButton("💰 贡献", callback_data="sect_contribution"),
             InlineKeyboardButton("🛡️ 护宗大阵", callback_data="sect_defense")],
            [InlineKeyboardButton("🎁 贡献法宝", callback_data="sect_contribute_artifact"),
             InlineKeyboardButton("📤 撤回法宝", callback_data="sect_withdraw_artifact")],
            [InlineKeyboardButton("👥 成员列表", callback_data="sect_members")]
        ])
        
        if is_leader:
            keyboard.append([InlineKeyboardButton("⚙️ 宗门管理", callback_data="sect_manage")])
        
        keyboard.append([InlineKeyboardButton("🚪 退出宗门", callback_data="sect_leave")])
    
    keyboard.append([InlineKeyboardButton("🔙 返回", callback_data="back_to_main")])
    return InlineKeyboardMarkup(keyboard)

def hunt_difficulty_keyboard():
    """刷怪难度选择键盘"""
    keyboard = [
        [InlineKeyboardButton("😊 简单 (受伤率10%)", callback_data="hunt_简单")],
        [InlineKeyboardButton("😐 普通 (受伤率30%)", callback_data="hunt_普通")],
        [InlineKeyboardButton("😰 困难 (受伤率60%)", callback_data="hunt_困难")],
        [InlineKeyboardButton("🔙 返回", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def retreat_time_keyboard():
    """闭关时间选择键盘"""
    keyboard = []
    times = [1, 3, 6, 12, 24, 48]
    
    for i in range(0, len(times), 2):
        row = []
        for j in range(i, min(i+2, len(times))):
            time = times[j]
            text = f"{time}小时" if time < 24 else f"{time//24}天"
            row.append(InlineKeyboardButton(text, callback_data=f"retreat_{time}"))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🔙 返回", callback_data="back_to_main")])
    return InlineKeyboardMarkup(keyboard)

def world_selection_keyboard(worlds: List[Dict], current_world_level: int):
    """世界选择键盘"""
    keyboard = []
    
    for world_level in range(1, 6):
        if current_world_level >= world_level:
            level_worlds = [w for w in worlds if w.world_level == world_level]
            if level_worlds:
                for world in level_worlds:
                    keyboard.append([InlineKeyboardButton(
                        f"🌍 {world.name} (等级{world_level})", 
                        callback_data=f"goto_world_{world.name}"
                    )])
    
    keyboard.append([InlineKeyboardButton("🔙 返回", callback_data="back_to_main")])
    return InlineKeyboardMarkup(keyboard)

def pagination_keyboard(current_page: int, total_pages: int, prefix: str):
    """分页键盘"""
    keyboard = []
    
    # 分页按钮
    if total_pages > 1:
        page_buttons = []
        if current_page > 1:
            page_buttons.append(InlineKeyboardButton("⬅️", callback_data=f"{prefix}_page_{current_page-1}"))
        
        page_buttons.append(InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="noop"))
        
        if current_page < total_pages:
            page_buttons.append(InlineKeyboardButton("➡️", callback_data=f"{prefix}_page_{current_page+1}"))
        
        keyboard.append(page_buttons)
    
    return keyboard

def back_keyboard(callback_data: str = "back_to_main"):
    """返回按钮键盘"""
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 返回", callback_data=callback_data)]])

def confirm_keyboard(action: str, item_id: str = ""):
    """确认操作键盘"""
    confirm_data = f"confirm_{action}_{item_id}" if item_id else f"confirm_{action}"
    cancel_data = f"cancel_{action}_{item_id}" if item_id else f"cancel_{action}"
    
    keyboard = [
        [InlineKeyboardButton("✅ 确认", callback_data=confirm_data),
         InlineKeyboardButton("❌ 取消", callback_data=cancel_data)]
    ]
    return InlineKeyboardMarkup(keyboard)