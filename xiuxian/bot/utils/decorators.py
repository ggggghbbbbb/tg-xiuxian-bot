from functools import wraps
from database.database import GameDatabase
import config

def require_registration(func):
    """需要注册的装饰器"""
    @wraps(func)
    async def wrapper(update, context):
        user_id = update.effective_user.id
        db = GameDatabase(config.DATABASE_PATH)
        player = db.get_player(user_id)
        
        if not player:
            await update.message.reply_text(
                "你还没有开始修仙之旅！\n"
                "请使用 /start 命令开始游戏。"
            )
            return
        
        return await func(update, context, player, db)
    return wrapper

def require_admin(func):
    """需要管理员权限的装饰器"""
    @wraps(func)
    async def wrapper(update, context):
        user_id = update.effective_user.id
        db = GameDatabase(config.DATABASE_PATH)
        
        if not db.is_admin(user_id) and user_id not in config.ADMIN_IDS:
            await update.message.reply_text("❌ 你没有管理员权限！")
            return
        
        return await func(update, context, db)
    return wrapper

def require_private_chat(func):
    """需要私聊的装饰器"""
    @wraps(func)
    async def wrapper(update, context):
        if update.effective_chat.type != 'private':
            await update.message.reply_text("此命令只能在私聊中使用！")
            return
        return await func(update, context)
    return wrapper