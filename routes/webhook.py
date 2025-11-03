"""
Telegram webhook endpoint for handling bot updates.
Processes incoming messages and commands from Telegram.
"""

from flask import Blueprint, request, jsonify, current_app
from telegram import Update

from core.logger import setup_logger

logger = setup_logger(__name__)

webhook_bp = Blueprint('webhook', __name__, url_prefix='/api')

@webhook_bp.route('/webhook', methods=['POST'])
def webhook():
    """Handle Telegram webhook updates"""
    try:
        # Access bot and application from Flask app context
        bot = current_app.config.get('BOT')
        application = current_app.config.get('APPLICATION')
        
        if not bot or not application:
            return jsonify({'error': 'Bot not configured'}), 500
            
        update = Update.de_json(request.get_json(), bot)
        
        # Process the update through the application
        if update:
            application.process_update(update)
            
        return jsonify({'status': 'ok'})
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 400
