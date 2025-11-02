"""
Health and info endpoints for the Telegram bot application.
Provides application status information.
"""

from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__, url_prefix='/api')

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Check application health status"""
    try:
        # Basic health checks
        return jsonify({
            'status': 'healthy',
            'service': 'content-hub-bot',
            'version': '1.0.0'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500
