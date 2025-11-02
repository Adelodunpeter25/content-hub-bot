"""
Application configuration management.
Handles environment variables and application settings validation.
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    BACKEND_API_URL = os.getenv('BACKEND_API_URL')
    FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    
    # App settings
    FEED_INTERVAL_MINUTES = 20
    MAX_FEEDS_PER_MESSAGE = 5
    REQUEST_TIMEOUT = 10
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required = ['TELEGRAM_BOT_TOKEN', 'BACKEND_API_URL', 'FLASK_SECRET_KEY']
        missing = [key for key in required if not getattr(cls, key)]
        if missing:
            raise ValueError(f"Missing required config: {', '.join(missing)}")
        return True
