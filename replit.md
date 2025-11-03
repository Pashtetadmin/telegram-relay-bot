# FastReel AI - Telegram Relay Bot

## Overview
A Python-based Telegram relay bot that facilitates customer communication by forwarding user messages to an admin and routing admin replies back to users. The bot supports text, photos, files, and voice messages, with complete conversation logging.

**Current State**: ✅ Fully functional and running

## Recent Changes
- **November 2, 2025**: Initial project setup
  - Created main bot logic with aiogram 2.25.1
  - Implemented message forwarding and reply routing system
  - Added CSV-based conversation logging
  - Set up Flask keep-alive server on port 3000
  - Configured Telegram Bot workflow

## Project Architecture

### Core Components
1. **main.py**: Main bot application
   - Handles Telegram bot initialization
   - Routes messages between users and admin
   - Implements anti-spam rate limiting (1 second per user)
   - Manages conversation logging

2. **keep_alive.py**: HTTP health check server
   - Flask server running on port 3000
   - Provides `/` endpoint for uptime monitoring
   - Prevents bot from sleeping on Replit

3. **dialog_log.csv**: Conversation log (auto-generated)
   - Tracks all messages with timestamps
   - Records user IDs, names, message types, and content

### Key Features
- **Message Forwarding**: User messages → Admin with user identification
- **Reply Routing**: Admin replies (via Telegram reply) → Original user
- **Multi-format Support**: Text, photos, files, voice messages
- **Rate Limiting**: 1-second cooldown per user to prevent spam
- **Conversation Logging**: Complete CSV logs with timestamps
- **Bot Commands**:
  - `/start` or `/help`: Welcome message and instructions
  - `/order`: Display website, payment, and form links

### Environment Variables (Required)
- `BOT_TOKEN`: Telegram bot token from @BotFather
- `ADMIN_ID`: Admin's Telegram user ID from @userinfobot
- `PORT`: HTTP server port (default: 3000)

### Dependencies
- `aiogram==2.25.1`: Telegram Bot API framework
- `python-dotenv==1.0.1`: Environment variable management
- `Flask==3.0.0`: HTTP server for keep-alive functionality

## How It Works
1. User sends a message to the bot
2. Bot forwards the message to admin with user's name and ID
3. Admin replies by replying to the forwarded message in Telegram
4. Bot detects the reply and sends it back to the original user
5. All interactions are logged to `dialog_log.csv`

## Customization
To update the bot's messages or links, edit these sections in `main.py`:
- Welcome message: Line 30-35 (`start_cmd` function)
- Order links: Line 40-45 (`order_cmd` function)

## Deployment
The bot is configured to run automatically on Replit. For 24/7 uptime:
1. Use UptimeRobot or cron-job.org
2. Ping your Replit URL every 5 minutes
3. Endpoint to ping: `https://YOUR-REPL-URL/`
