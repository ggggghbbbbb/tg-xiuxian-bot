from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.database import GameDatabase
from database.models import Player
from bot.keyboards.panels import *
from bot.utils.game_logic import GameLogic
from datetime import datetime
import config

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """开始游戏命令"""
    user = update.effective_user
    db = GameDatabase(config.DATABASE_PATH)
    
    # 检查是否已注册
    existing_player = db.get_player(user.id)
    if existing_player:
        is_admin = db.is_admin(user.id) or user.id in config.ADMIN_IDS
        await update.message.reply_text(
            f"🎉 欢迎回来，{existing_player.name}！\n"
            f"📊 等级：{existing_player.level}\n"
            f"🌍 当前世界：{existing_player.world or '未选择'}\n"
            f"⚡ 经验：{existing_player.exp}\n\n"
            "点击下方按钮打开面板：",
            reply_markup=main_panel_keyboard(is_admin)
        )
        return
    
    # 创建新玩家
    player = Player(
        tg_id=user.id,
        username=user.username or "",
        name=user.first_name or "修仙者"
    )
    
    if db.create_player(player):
        is_admin = db.is_admin(user.id) or user.id in config.ADMIN_IDS
        await update.message.reply_text(
            f"🎉 欢迎踏入修仙世界，{player.name}！\n\n"
            f"📊 等级：{player.level}\n"
            f"⚡ 经验：{player.exp}\n"
            f"💰 初始灵石：{player.spirit_stones.get('下品灵石', 1000)}\n\n"
            "你的修仙之旅正式开始！\n"
            "使用 /name 新名字 来修改角色名\n"
            "点击下方按钮打开面板：",
            reply_markup=main_panel_keyboard(is_admin)
        )
    else:
        await update.message.reply_text("创建角色失败，请稍后重试。")

async def panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """面板命令"""
    if update.effective_chat.type != 'private':
        await update.message.reply_text("此命令只能在私聊中使用！")
        return
    
    user_id = update.effective_user.id
    db = GameDatabase(config.DATABASE_PATH)
    
    is_admin = db.is_admin(user_id) or user_id in config.ADMIN_IDS
    await update.message.reply_text(
        "🎮 修仙世界主面板\n\n"
        "选择你要进行的操作：",
        reply_markup=main_panel_keyboard(is_admin)
    )

async def name_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """修改角色名命令"""
    if update.effective_chat.type != 'private':
        await update.message.reply_text("此命令只能在私聊中使用！")
        return
    
    if not context.args:
        await update.message.reply_text("使用格式：/name 新的角色名")
        return
    
    user_id = update.effective_user.id
    db = GameDatabase(config.DATABASE_PATH)
    player = db.get_player(user_id)
    
    if not player:
        await update.message.reply_text("请先使用 /start 创建角色！")
        return
    
    new_name = " ".join(context.args)
    if len(new_name) > 20:
        await update.message.reply_text("角色名不能超过20个字符！")
        return
    
    old_name = player.name
    player.name = new_name
    
    if db.update_player(player):
        await update.message.reply_text(f"✅ 角色名已从 {old_name} 修改为 {new_name}！")
    else:
        await update.message.reply_text("❌ 修改失败，请稍后重试。")

async def use_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """使用物品命令"""
    if update.effective_chat.type != 'private':
        await update.message.reply_text("此命令只能在私聊中使用！")
        return
    
    if not context.args:
        await update.message.reply_text("使用格式：/use 物品名")
        return
    
    user_id = update.effective_user.id
    db = GameDatabase(config.DATABASE_PATH)
    player = db.get_player(user_id)
    
    if not player:
        await update.message.reply_text("请先使用 /start 创建角色！")
        return
    
    item_name = " ".join(context.args)
    game_logic = GameLogic(db)
    
    success, message = game_logic.use_item(player, item_name)
    if success:
        db.update_player(player)
        
        # 检查是否可以升级
        while game_logic.can_level_up(player):
            game_logic.level_up(player)
            message += f"\n🎉 升级到 {player.level} 级！"
        
        db.update_player(player)
    
    await update.message.reply_text(f"{'✅' if success else '❌'} {message}")

async def equip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """装备物品命令"""
    if update.effective_chat.type != 'private':
        await update.message.reply_text("此命令只能在私聊中使用！")
        return
    
    if not context.args:
        await update.message.reply_text("使用格式：/equip 装备名")
        return
    
    user_id = update.effective_user.id
    db = GameDatabase(config.DATABASE_PATH)
    player = db.get_player(user_id)
    
    if not player:
        await update.message.reply_text("请先使用 /start 创建角色！")
        return
    
    equip_name = " ".join(context.args)
    game_logic = GameLogic(db)
    
    success, message = game_logic.equip_item(player, equip_name)
    if success:
        db.update_player(player)
    
    await update.message.reply_text(f"{'✅' if success else '❌'} {message}")

async def battle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """比武命令 (群聊使用)"""
    if update.effective_chat.type == 'private':
        await update.message.reply_text("比武命令只能在群聊中使用！")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("请回复要挑战的玩家消息使用此命令！")
        return
    
    challenger_id = update.effective_user.id
    target_id = update.message.reply_to_message.from_user.id
    
    if challenger_id == target_id:
        await update.message.reply_text("不能挑战自己！")
        return
    
    db = GameDatabase(config.DATABASE_PATH)
    challenger = db.get_player(challenger_id)
    target = db.get_player(target_id)
    
    if not challenger:
        await update.message.reply_text("你还没有创建角色！请私聊bot使用 /start")
        return
    
    if not target:
        await update.message.reply_text("对方还没有创建角色！")
        return
    
    # 检查状态
    if challenger.status.get('injured', False) or challenger.status.get('retreating', False):
        await update.message.reply_text("你当前状态无法比武！")
        return
    
    if target.status.get('injured', False) or target.status.get('retreating', False):
        await update.message.reply_text("对方当前状态无法比武！")
        return
    
    # 创建比武邀请
    keyboard = [
        [InlineKeyboardButton("⚔️ 接受挑战", callback_data=f"accept_battle_{challenger_id}_{target_id}")],
        [InlineKeyboardButton("❌ 拒绝挑战", callback_data=f"reject_battle_{challenger_id}_{target_id}")]
    ]
    
    await update.message.reply_text(
        f"⚔️ {challenger.name} 向 {target.name} 发起比武挑战！\n\n"
        f"挑战者战力：{GameLogic(db).calculate_combat_power(challenger)}\n"
        f"被挑战者战力：{GameLogic(db).calculate_combat_power(target)}\n\n"
        f"@{update.message.reply_to_message.from_user.username or target.name} 请选择：",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )