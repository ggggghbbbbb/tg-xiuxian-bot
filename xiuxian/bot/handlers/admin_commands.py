from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.database import GameDatabase
from database.models import World, Equipment, Item, Sect
from bot.utils.decorators import require_admin
import config
import json

@require_admin
async def admin_create_world_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: GameDatabase):
    """管理员创建世界命令"""
    if len(context.args) < 3:
        await update.message.reply_text(
            "使用格式：/admin_world 世界名 世界等级 描述\n"
            "示例：/admin_world 仙界 2 仙人居住的神秘世界"
        )
        return
    
    world_name = context.args[0]
    try:
        world_level = int(context.args[1])
    except ValueError:
        await update.message.reply_text("世界等级必须是数字！")
        return
    
    description = " ".join(context.args[2:])
    
    if world_level not in config.WORLD_LEVELS:
        await update.message.reply_text(f"世界等级必须在1-5之间！")
        return
    
    world = World(
        name=world_name,
        world_level=world_level,
        description=description
    )
    
    if db.create_world(world):
        await update.message.reply_text(f"✅ 成功创建世界：{world_name} (等级{world_level})")
    else:
        await update.message.reply_text("❌ 创建世界失败！")

@require_admin
async def admin_create_equipment_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: GameDatabase):
    """管理员创建装备命令"""
    if len(context.args) < 6:
        await update.message.reply_text(
            "使用格式：/admin_equip 装备名 部位 品质 等级要求 世界等级要求 属性JSON [描述]\n"
            "部位：" + "，".join(config.ALL_SLOTS.keys()) + "\n"
            "品质：" + "，".join(config.EQUIPMENT_QUALITIES) + "\n"
            "示例：/admin_equip 神剑 武器 传说 20 2 '{\"攻击力\":100,\"暴击率\":5}' 传说中的神器"
        )
        return
    
    equip_name = context.args[0]
    slot = context.args[1]
    quality = context.args[2]
    
    try:
        level_req = int(context.args[3])
        world_level_req = int(context.args[4])
        attributes = json.loads(context.args[5])
    except (ValueError, json.JSONDecodeError) as e:
        await update.message.reply_text(f"参数错误：{e}")
        return
    
    if slot not in config.ALL_SLOTS:
        await update.message.reply_text(f"无效部位！可用部位：{', '.join(config.ALL_SLOTS.keys())}")
        return
    
    if quality not in config.EQUIPMENT_QUALITIES:
        await update.message.reply_text(f"无效品质！可用品质：{', '.join(config.EQUIPMENT_QUALITIES)}")
        return
    
    description = " ".join(context.args[6:]) if len(context.args) > 6 else ""
    
    equipment = Equipment(
        name=equip_name,
        slot=slot,
        quality=quality,
        level_requirement=level_req,
        world_level_requirement=world_level_req,
        description=description,
        attributes=attributes
    )
    
    if db.create_equipment(equipment):
        await update.message.reply_text(f"✅ 成功创建装备：{equip_name}")
    else:
        await update.message.reply_text("❌ 创建装备失败！")

@require_admin
async def admin_create_item_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: GameDatabase):
    """管理员创建物品命令"""
    if len(context.args) < 4:
        await update.message.reply_text(
            "使用格式：/admin_item 物品名 类型 效果JSON [描述]\n"
            "类型：消耗品，材料，特殊\n"
            "示例：/admin_item 力量药水 消耗品 '{\"攻击力\":10,\"经验\":50}' 增加10点攻击力和50经验"
        )
        return
    
    item_name = context.args[0]
    item_type = context.args[1]
    
    try:
        effects = json.loads(context.args[2])
    except json.JSONDecodeError as e:
        await update.message.reply_text(f"效果JSON格式错误：{e}")
        return
    
    description = " ".join(context.args[3:]) if len(context.args) > 3 else ""
    
    # 创建物品
    with db.get_connection() as conn:
        conn.execute('''
            INSERT OR REPLACE INTO items (name, item_type, description, effects, usable)
            VALUES (?, ?, ?, ?, ?)
        ''', (item_name, item_type, description, json.dumps(effects), True))
        conn.commit()
    
    await update.message.reply_text(f"✅ 成功创建物品：{item_name}")

@require_admin
async def admin_grant_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: GameDatabase):
    """管理员给予物品命令"""
    if len(context.args) < 3:
        await update.message.reply_text(
            "使用格式：/admin_grant 用户ID 物品名 数量\n"
            "示例：/admin_grant 123456789 神剑 1"
        )
        return
    
    try:
        user_id = int(context.args[0])
        quantity = int(context.args[2])
    except ValueError:
        await update.message.reply_text("用户ID和数量必须是数字！")
        return
    
    item_name = context.args[1]
    
    # 检查用户是否存在
    player = db.get_player(user_id)
    if not player:
        await update.message.reply_text("用户不存在！")
        return
    
    # 检查物品是否存在
    item = db.get_item(item_name)
    equipment = db.get_equipment(item_name)
    
    if not item and not equipment:
        await update.message.reply_text("物品/装备不存在！")
        return
    
    # 给予物品
    player.inventory[item_name] = player.inventory.get(item_name, 0) + quantity
    
    if db.update_player(player):
        await update.message.reply_text(
            f"✅ 已给予 {player.name}({user_id}) {item_name} x{quantity}"
        )
    else:
        await update.message.reply_text("❌ 给予物品失败！")

@require_admin
async def admin_teleport_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: GameDatabase):
    """管理员传送玩家命令"""
    if len(context.args) < 2:
        await update.message.reply_text(
            "使用格式：/admin_tp 用户ID 世界名\n"
            "示例：/admin_tp 123456789 仙界"
        )
        return
    
    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("用户ID必须是数字！")
        return
    
    world_name = context.args[1]
    
    # 检查用户是否存在
    player = db.get_player(user_id)
    if not player:
        await update.message.reply_text("用户不存在！")
        return
    
    # 检查世界是否存在
    with db.get_connection() as conn:
        world_exists = conn.execute(
            'SELECT 1 FROM worlds WHERE name = ?', (world_name,)
        ).fetchone()
    
    if not world_exists:
        await update.message.reply_text("世界不存在！")
        return
    
    player.world = world_name
    
    if db.update_player(player):
        await update.message.reply_text(f"✅ 已将 {player.name} 传送到 {world_name}")
    else:
        await update.message.reply_text("❌ 传送失败！")