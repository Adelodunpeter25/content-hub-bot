"""
Telegram bot service for handling user interactions.
Manages bot commands and user subscription lifecycle.
"""

from telegram import Update
from telegram.ext import ContextTypes

from .feed_service import FeedService
from core.logger import setup_logger

logger = setup_logger(__name__)

class TelegramService:
    def __init__(self, feed_service: FeedService, subscribers: set):
        self.feed_service = feed_service
        self.subscribers = subscribers

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        chat_id = update.effective_chat.id
        self.subscribers.add(chat_id)
        await update.message.reply_text(
            "Welcome! You'll receive feed updates every 20 minutes.\n"
            "Commands:\n/feeds - Get all feeds\n/latest - Get 3 most recent\n/stop - Unsubscribe"
        )

    async def get_feeds(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /feeds command"""
        feeds = self.feed_service.fetch_feeds()
        if feeds:
            message = self.feed_service.format_feeds(feeds)
            await update.message.reply_text(message, parse_mode='HTML', disable_web_page_preview=True)
        else:
            await update.message.reply_text("Sorry, couldn't fetch feeds right now.")

    async def get_latest(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /latest command - shows only 3 most recent feeds"""
        feeds = self.feed_service.fetch_feeds()
        if feeds:
            # Get only the 3 most recent feeds
            latest_feeds = feeds[:3]
            message = self.feed_service.format_feeds(latest_feeds, title="🔥 Latest Updates")
            await update.message.reply_text(message, parse_mode='HTML', disable_web_page_preview=True)
        else:
            await update.message.reply_text("Sorry, couldn't fetch feeds right now.")

    async def stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stop command"""
        chat_id = update.effective_chat.id
        self.subscribers.discard(chat_id)
        await update.message.reply_text("You've been unsubscribed from feed updates.")
