# FastReel Support Bot - Project Summary

## 🎯 Project Overview

This is a **webhook-based Telegram bot** designed for customer support, optimized for deployment on **Railway**. The bot forwards user messages to an admin and allows the admin to reply using command-based system.

## 📁 Project Structure

### Railway Deployment Files (Main Project)
- **main_webhook.py** - Webhook-based bot using aiohttp server
- **requirements.txt** - Python dependencies (aiogram 2.25.1, aiohttp, python-dotenv)
- **Procfile** - Railway process configuration
- **runtime.txt** - Python version specification (3.11)
- **.env.example** - Environment variables template
- **README_RAILWAY.md** - Complete Railway deployment guide

### Backup Files
- **old_polling_bot/** - Contains the previous polling-based bot (main.py, keep_alive.py)
  - This was the original implementation using long-polling
  - Kept for reference but not used in Railway deployment

### Other Files
- **README.md** - Original project documentation
- **replit.md** - Replit project memory/documentation
- **dialog_log.csv** - Conversation logs (auto-generated)

## 🔑 Key Differences: Webhook vs Polling Bot

| Feature | Webhook Bot (Railway) | Polling Bot (Replit) |
|---------|----------------------|---------------------|
| **Method** | Webhooks | Long polling |
| **Server** | aiohttp web server | Flask keep-alive |
| **Platform** | Railway optimized | Replit optimized |
| **Reply System** | `/r <user_id> <message>` command | Reply to forwarded messages |
| **Scalability** | Better (event-driven) | Limited (constant polling) |
| **Resource Usage** | Lower | Higher |

## 🚀 How to Deploy

### Railway (Recommended for Production)
1. Follow instructions in **README_RAILWAY.md**
2. Deploy to Railway with webhook support
3. Use `/r <user_id> <message>` to reply to users

### Replit (For Development/Testing)
1. Use the files in **old_polling_bot/**
2. Set up secrets: BOT_TOKEN, ADMIN_ID
3. Reply directly to forwarded messages in Telegram

## 📝 Environment Variables

Both implementations require:
- **BOT_TOKEN** - From @BotFather
- **ADMIN_ID** - Your Telegram user ID

Webhook bot additionally needs:
- **PUBLIC_BASE_URL** - Your Railway app URL
- **PORT** - Server port (Railway sets this automatically)

## 🔄 Migration Path

If migrating from polling bot to webhook bot:
1. Deploy webhook bot to Railway
2. Update PUBLIC_BASE_URL with Railway domain
3. Bot will automatically set webhook
4. Old polling bot can be stopped

## 📊 Features

✅ Message forwarding (user → admin)
✅ Admin reply system
✅ Support for text, photos, files, voice
✅ Conversation logging
✅ Health check endpoint
✅ Auto-webhook setup
✅ Production-ready error handling

## 🎯 Current Status

- ✅ Webhook bot fully implemented and ready for Railway
- ✅ All deployment files created
- ✅ Comprehensive documentation provided
- ✅ Old polling bot backed up for reference
- ⏳ Ready for Railway deployment by user

## 📞 Bot Commands

### Users:
- `/start` - Welcome message
- `/order` - View links (website, payment, form)

### Admin:
- `/r <user_id> <message>` - Reply to specific user
  - Example: `/r 123456789 Hello! How can I help?`

## 🛠️ Technology Stack

- **Python 3.11**
- **aiogram 2.25.1** - Telegram Bot API framework
- **aiohttp 3.8.6** - Async HTTP server for webhooks
- **python-dotenv 1.0.1** - Environment variable management

## 📦 Deployment Platforms

- **Primary**: Railway (webhook bot)
- **Alternative**: Replit (polling bot - for development only)

---

**Next Step**: Deploy to Railway following README_RAILWAY.md instructions! 🚀
