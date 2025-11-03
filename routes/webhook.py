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
        logger.info(f"Webhook received: {request.get_json()}")
        
        # Access services from Flask app context
        bot = current_app.config.get('BOT')
        telegram_service = current_app.config.get('TELEGRAM_SERVICE')
        
        if not bot or not telegram_service:
            logger.error("Bot or telegram_service not configured")
            return jsonify({'error': 'Bot not configured'}), 500
            
        update = Update.de_json(request.get_json(), bot)
        logger.info(f"Parsed update: {update}")
        
        # Process the update manually
        if update and update.message:
            message = update.message
            logger.info(f"Processing message: {message.text}")
            if message.text:
                # Run async methods in a new event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    if message.text.startswith('/start'):
                        logger.info("Processing /start command")
                        loop.run_until_complete(telegram_service.start(update, None))
                    elif message.text.startswith('/feeds'):
                        logger.info("Processing /feeds command")
                        loop.run_until_complete(telegram_service.get_feeds(update, None))
                    elif message.text.startswith('/latest'):
                        logger.info("Processing /latest command")
                        loop.run_until_complete(telegram_service.get_latest(update, None))
                    elif message.text.startswith('/stop'):
                        logger.info("Processing /stop command")
                        loop.run_until_complete(telegram_service.stop(update, None))
                finally:
                    loop.close()
            
        return jsonify({'status': 'ok'})
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 400
