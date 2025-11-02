"""
Telegram webhook endpoint for handling bot updates.
Processes incoming messages and commands from Telegram.
"""

from flask import Blueprint, request, jsonify
from telegram import Update

from core.logger import setup_logger
from main import bot, application

logger = setup_logger(__name__)

webhook_bp = Blueprint('webhook', __name__, url_prefix='/api')

@webhook_bp.route('/webhook', methods=['POST'])
def webhook():
    """Handle Telegram webhook updates"""
    try:
        update = Update.de_json(request.get_json(), bot)   
        # Process the update through the application
        if update:
            application.process_update(update)
            
        return jsonify({'status': 'ok'})
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 400
