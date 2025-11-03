"""
Content Hub Telegram Bot - Main Application

A Flask-based Telegram bot that fetches feeds from Content Hub API every 20 minutes
and sends updates to subscribed users. Provides health monitoring and webhook endpoints.
"""

import os
import sys
import asyncio
from flask import Flask
from telegram import Bot
from telegram.ext import Application, CommandHandler

from core.config import Config
from core.logger import setup_logger
from services.feed_service import FeedService
from services.telegram_service import TelegramService
from services.scheduler_service import SchedulerService
from routes.health import health_bp
from routes.info import info_bp
from routes.webhook import webhook_bp

# Validate configuration
Config.validate()

logger = setup_logger(__name__)

app = Flask(__name__)
app.secret_key = Config.FLASK_SECRET_KEY

# Register blueprints
app.register_blueprint(health_bp)
app.register_blueprint(info_bp)
app.register_blueprint(webhook_bp)

# Global state - moved to avoid circular imports
subscribers = set()

# Store services in app config to avoid circular imports
def init_services():
    """Initialize services when needed"""
    if 'SERVICES_INITIALIZED' not in app.config:
        bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
        feed_service = FeedService(Config.BACKEND_API_URL)
        telegram_service = TelegramService(feed_service, subscribers)
        scheduler_service = SchedulerService(bot, feed_service, subscribers)
        
        app.config['BOT'] = bot
        app.config['FEED_SERVICE'] = feed_service
        app.config['TELEGRAM_SERVICE'] = telegram_service
        app.config['SCHEDULER_SERVICE'] = scheduler_service
        app.config['SUBSCRIBERS'] = subscribers
        app.config['SERVICES_INITIALIZED'] = True
    
    return app.config

def setup_webhook():
    """Setup Telegram webhook for production"""
    webhook_url = "https://content-hub-bot.onrender.com/api/webhook"
    async def set_webhook():
        bot = app.config['BOT']
        try:
            await bot.set_webhook(url=webhook_url)
            logger.info(f"Webhook set to: {webhook_url}")
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(set_webhook())
    finally:
        loop.close()

init_services()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'polling':
        # Run in polling mode for development
        logger.info("Starting bot in polling mode...")
        logger.info("Bot is running. Press Ctrl+C to stop.")
        
        # Create application only when needed for polling
        application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        telegram_service = app.config['TELEGRAM_SERVICE']
        application.add_handler(CommandHandler("start", telegram_service.start))
        application.add_handler(CommandHandler("feeds", telegram_service.get_feeds))
        application.add_handler(CommandHandler("latest", telegram_service.get_latest))
        application.add_handler(CommandHandler("stop", telegram_service.stop))
        
        application.run_polling()
    else:
        # Run Flask server (webhook mode) with scheduler
        scheduler_service = app.config['SCHEDULER_SERVICE']
        scheduler = scheduler_service.setup_scheduler(app)
        
        # Setup webhook for production
        setup_webhook()
        
        port = int(os.environ.get('PORT'))
        logger.info(f"Starting Flask server on port {port}")
        try:
            app.run(host='0.0.0.0', port=port, debug=False)
        except KeyboardInterrupt:
            scheduler_service.shutdown()
