"""
Application information endpoint.
Provides service metadata and statistics.
"""

import os
from flask import Blueprint, jsonify
from flask import current_app

info_bp = Blueprint('info', __name__, url_prefix='/api')

@info_bp.route('/info', methods=['GET'])
def info():
    """Get application information and statistics"""
    subscribers = current_app.config.get('SUBSCRIBERS', set())
    return jsonify({
        'service': 'content-hub-bot',
        'version': '1.0.0',
        'subscribers': len(subscribers),
        'backend_url': os.getenv('BACKEND_API_URL', 'Not configured'),
        'feed_interval_minutes': 20
    })
