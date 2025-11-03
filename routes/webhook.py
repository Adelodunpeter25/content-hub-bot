"""
Telegram webhook endpoint for handling bot updates.
Processes incoming messages and commands from Telegram.
"""

import asyncio
from flask import Blueprint, request, jsonify, current_app
from telegram import Update

from core.logger import setup_logger

logger = setup_logger(__name__)

webhook_bp = Blueprint('webhook', __name__, url_prefix='/api')

@webhook_bp.route('/webhook', methods=['POST'])
def webhook():
    """Handle Telegram webhook updates"""
    try:
        # Access services from Flask app context
        bot = current_app.config.get('BOT')
        telegram_service = current_app.config.get('TELEGRAM_SERVICE')
        
        if not bot or not telegram_service:
            return jsonify({'error': 'Bot not configured'}), 500
            
        update = Update.de_json(request.get_json(), bot)
        
        # Process the update manually
        if update and update.message:
            message = update.message
            if message.text:
                # Run async methods in a new event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    if message.text.startswith('/start'):
                        loop.run_until_complete(telegram_service.start(update, None))
                    elif message.text.startswith('/feeds'):
                        loop.run_until_complete(telegram_service.get_feeds(update, None))
                    elif message.text.startswith('/stop'):
                        loop.run_until_complete(telegram_service.stop(update, None))
                finally:
                    loop.close()
            
        return jsonify({'status': 'ok'})
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 400
