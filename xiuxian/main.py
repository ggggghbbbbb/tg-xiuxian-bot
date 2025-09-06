import logging
import asyncio
import os
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from bot.handlers.user_commands import *
from bot.handlers.admin_commands import *
from bot.handlers.callbacks import callback_handler
from database.database import GameDatabase
import config

# 设置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def ensure_data_directory():
    """确保data目录存在"""
    data_dir = os.path.dirname(config.DATABASE_PATH)
    if data_dir and not os.path.exists(data_dir):
        os.makedirs(data_dir)

def main():
    """启动Bot"""
    logger.info("开始启动修仙Bot...")
    
    # 确保数据目录存在
    ensure_data_directory()
    
    # 初始化数据库
    db = GameDatabase(config.DATABASE_PATH)
    logger.info("数据库初始化完成")
    
    # 创建应用
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # 用户命令
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("panel", panel_command))
    application.add_handler(CommandHandler("name", name_command))
    application.add_handler(CommandHandler("use", use_command))
    application.add_handler(CommandHandler("equip", equip_command))
    
    # 管理员命令
    application.add_handler(CommandHandler("admin_world", admin_create_world_command))
    application.add_handler(CommandHandler("admin_equip", admin_create_equipment_command))
    application.add_handler(CommandHandler("admin_item", admin_create_item_command))
    application.add_handler(CommandHandler("admin_grant", admin_grant_command))
    application.add_handler(CommandHandler("admin_tp", admin_teleport_command))
    
    # 回调处理
    application.add_handler(CallbackQueryHandler(callback_handler))
    
    logger.info("Bot启动成功，开始轮询...")
    
    # 启动Bot
    application.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == '__main__':
    main()