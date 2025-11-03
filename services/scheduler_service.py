"""
Scheduler service for periodic feed broadcasting.
Handles automated feed fetching and distribution to subscribers.
"""

import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Bot

from core.config import Config
from core.logger import setup_logger
from .feed_service import FeedService

logger = setup_logger(__name__)

class SchedulerService:
    def __init__(self, bot: Bot, feed_service: FeedService, subscribers: set):
        self.bot = bot
        self.feed_service = feed_service
        self.subscribers = subscribers
        self.scheduler = None

    async def send_feeds_to_subscribers(self):
        """Send latest feeds to all subscribers"""
        if not self.subscribers:
            return
            
        feeds = self.feed_service.fetch_feeds()
        if not feeds:
            return
            
        message = self.feed_service.format_feeds(feeds)
        
        for chat_id in self.subscribers.copy():
            try:
                await self.bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML', disable_web_page_preview=True)
            except Exception as e:
                logger.error(f"Failed to send to {chat_id}: {e}")
                self.subscribers.discard(chat_id)

    def _run_async_job(self):
        """Run async job in new event loop"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.send_feeds_to_subscribers())
        finally:
            loop.close()
    
    def setup_scheduler(self, app):
        """Setup background scheduler for periodic feed fetching"""
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            func=self._run_async_job,
            trigger="interval",
            minutes=Config.FEED_INTERVAL_MINUTES,
            id='fetch_feeds'
        )
        self.scheduler.start()
        return self.scheduler

    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler:
            self.scheduler.shutdown()
