from flask import Flask, request, jsonify
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler
from core.config import Config
from core.logger import setup_logger
from services.feed_service import FeedService
from services.telegram_service import TelegramService

# Validate configuration
Config.validate()

logger = setup_logger(__name__)

app = Flask(__name__)
app.secret_key = Config.FLASK_SECRET_KEY

bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
subscribers = set()

# Initialize services
feed_service = FeedService(Config.BACKEND_API_URL)
telegram_service = TelegramService(feed_service, subscribers)

async def send_feeds_to_subscribers():
    """Send latest feeds to all subscribers"""
    if not subscribers:
        return
        
    feeds = feed_service.fetch_feeds()
    if not feeds:
        return
        
    message = feed_service.format_feeds(feeds)
    
    for chat_id in subscribers.copy():
        try:
            await bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
        except Exception as e:
            logger.error(f"Failed to send to {chat_id}: {e}")
            subscribers.discard(chat_id)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'subscribers': len(subscribers)})

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle Telegram webhook"""
    try:
        update = Update.de_json(request.get_json(), bot)
        return jsonify({'status': 'ok'})
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 400

def setup_scheduler():
    """Setup background scheduler for periodic feed fetching"""
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=lambda: app.app_context().run(send_feeds_to_subscribers()),
        trigger="interval",
        minutes=Config.FEED_INTERVAL_MINUTES,
        id='fetch_feeds'
    )
    scheduler.start()
    return scheduler

if __name__ == '__main__':
    # Setup Telegram bot
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", telegram_service.start))
    application.add_handler(CommandHandler("feeds", telegram_service.get_feeds))
    application.add_handler(CommandHandler("stop", telegram_service.stop))
    
    # Setup scheduler
    scheduler = setup_scheduler()
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        scheduler.shutdown()
