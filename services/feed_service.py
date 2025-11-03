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
            url = f"{self.backend_url}/api/feeds"
            response = requests.get(url, timeout=Config.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            articles = data.get('articles', [])
            return articles
        except requests.RequestException as e:
            logger.error(f"Failed to fetch feeds: {e}")
            return None

    @staticmethod
    def format_feeds(feeds: List[Dict], title: str = None) -> str:
        """Format feeds for Telegram message"""
        if not feeds or not isinstance(feeds, list):
            return "No feeds available"
        
        if not title:
            title = f"📰 <b>Latest Articles</b>"
        
        message = f"{title}\n<i>{datetime.now().strftime('%B %d, %Y at %H:%M')}</i>\n\n"
        
        for i, feed in enumerate(feeds[:Config.MAX_FEEDS_PER_MESSAGE], 1):
            article_title = feed.get('title', 'No title')[:75]
            link = feed.get('link', '')
            source = feed.get('source', 'Unknown')
            summary = feed.get('summary', '').strip()[:140]
            categories = ', '.join(feed.get('categories', []))
            published = feed.get('published', '')
            
            # Article number and title
            message += f"<b>{i}. <a href='{link}'>{article_title}</a></b>\n"
            
            # Summary
            if summary:
                message += f"<i>{summary}...</i>\n"
            
            # Source and metadata
            message += f"📺 <b>{source}</b>"
            if categories:
                message += f" • 🏷️ {categories}"
            
            if published:
                try:
                    pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
                    message += f" • 📅 {pub_date.strftime('%m/%d %H:%M')}"
                except:
                    pass
            
            # Add separator between articles (except last one)
            if i < min(len(feeds), Config.MAX_FEEDS_PER_MESSAGE):
                message += "\n\n──────────\n\n"
            else:
                message += "\n"
            
        return message
