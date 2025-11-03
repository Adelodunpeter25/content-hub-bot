"""
Content Hub Telegram Bot - Main Application

A Flask-based Telegram bot that fetches feeds from Content Hub API every 20 minutes
and sends updates to subscribed users. Provides health monitoring and webhook endpoints.
"""

import sys
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

bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
subscribers = set()

# Initialize services
feed_service = FeedService(Config.BACKEND_API_URL)
telegram_service = TelegramService(feed_service, subscribers)
scheduler_service = SchedulerService(bot, feed_service, subscribers)

# Setup Telegram bot application
application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
application.add_handler(CommandHandler("start", telegram_service.start))
application.add_handler(CommandHandler("feeds", telegram_service.get_feeds))
application.add_handler(CommandHandler("stop", telegram_service.stop))

# Store in Flask config for webhook access
app.config['BOT'] = bot
app.config['APPLICATION'] = application

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'polling':
        # Run in polling mode for development
        logger.info("Starting bot in polling mode...")
        logger.info("Bot is running. Press Ctrl+C to stop.")
        application.run_polling()
    else:
        # Run Flask server (webhook mode) with scheduler
        scheduler = scheduler_service.setup_scheduler(app)
        try:
            app.run(host='0.0.0.0', port=5000, debug=True)
        except KeyboardInterrupt:
            scheduler_service.shutdown()
