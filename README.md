# Content Hub Telegram Bot

A Flask-based Telegram bot that fetches feeds from your backend API every 20 minutes.

## Setup

1. Copy `.env.example` to `.env` and fill in your values:
   ```bash
   cp .env.example .env
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Run the bot:
   ```bash
   uv run python main.py
   ```

## Environment Variables

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from @BotFather
- `BACKEND_API_URL`: Your backend API base URL
- `FLASK_SECRET_KEY`: Secret key for Flask sessions
- `PORT`: Port number for the Flask server (defaults to 5000)

## Bot Commands

- `/start` - Subscribe to feed updates
- `/feeds` - Get latest feeds manually
- `/stop` - Unsubscribe from updates

## API Endpoints

- `GET /health` - Health check and subscriber count
- `POST /webhook` - Telegram webhook endpoint
