"""
Feed service for backend API communication.
Handles fetching and formatting of feed data from Content Hub API.
"""

import requests
from datetime import datetime
from typing import Optional, List, Dict

from core.logger import setup_logger
from core.config import Config

logger = setup_logger(__name__)

class FeedService:
    def __init__(self, backend_url: str):
        self.backend_url = backend_url

    def fetch_feeds(self) -> Optional[List[Dict]]:
        """Fetch feeds from backend API"""
        try:
            response = requests.get(
                f"{self.backend_url}/feeds", 
                timeout=Config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch feeds: {e}")
            return None

    @staticmethod
    def format_feeds(feeds: List[Dict]) -> str:
        """Format feeds for Telegram message"""
        if not feeds or not isinstance(feeds, list):
            return "No feeds available"
            
        message = f"📰 <b>Latest Feeds</b> ({datetime.now().strftime('%H:%M')})\n\n"
        
        for feed in feeds[:Config.MAX_FEEDS_PER_MESSAGE]:
            title = feed.get('title', 'No title')[:100]
            url = feed.get('url', '')
            message += f"• <a href='{url}'>{title}</a>\n"
            
        return message
