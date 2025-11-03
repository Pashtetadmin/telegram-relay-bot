# FastReel Support Bot - Railway Deployment Guide

A webhook-based Telegram bot for customer support, designed for deployment on Railway.

## 📋 Features

- **Webhook-based** - Uses webhooks (not polling) for better performance and Railway compatibility
- **Message forwarding** - All user messages are forwarded to admin with user details
- **Admin reply system** - Admin can reply to users using `/r <user_id> <message>` command
- **Support for all content types** - Text, photos, files, voice messages, etc.
- **Health check endpoint** - `/` endpoint for Railway health checks
- **Production-ready** - Clean code, error handling, and logging

## 🚀 Railway Deployment Steps

### Step 1: Prepare Your Bot

1. **Create a Telegram Bot**:
   - Open Telegram and search for `@BotFather`
   - Send `/newbot` and follow the instructions
   - Copy your bot token (looks like: `123456789:ABCdefGHIjklMNOpqrSTUvwxyz`)

2. **Get Your Admin ID**:
   - Search for `@userinfobot` on Telegram
   - Send `/start` to get your user ID (a number like: `1234567890`)

### Step 2: Deploy to Railway

1. **Create a Railway Account**:
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Create New Project**:
   - Click "New Project"
   - Choose "Deploy from GitHub repo" or "Empty Project"

3. **Connect Your Repository** (if using GitHub):
   - Select your repository
   - Railway will auto-detect Python

   **OR Deploy from CLI**:
   ```bash
   npm install -g @railway/cli
   railway login
   railway init
   railway up
   ```

4. **Add Environment Variables**:
   Go to your Railway project → Variables → Add these:
   
   ```
   BOT_TOKEN=your_bot_token_from_botfather
   ADMIN_ID=your_telegram_user_id
   PUBLIC_BASE_URL=https://your-app.up.railway.app
   PORT=8080
   ```

   **Important**: For `PUBLIC_BASE_URL`, use your Railway domain. You can find it in:
   - Settings → Domains → Generate Domain
   - Copy the generated URL (e.g., `https://fastreel-support-bot-production.up.railway.app`)

5. **Deploy**:
   - Railway will automatically build and deploy your bot
   - Check the logs to ensure the webhook is set successfully
   - You should see: `✅ Webhook successfully set!`

### Step 3: Test Your Bot

1. **Find your bot on Telegram** (use the username you created with BotFather)
2. **Send a test message** to your bot
3. **Check your admin Telegram** - you should receive the forwarded message
4. **Reply using**: `/r <user_id> Your response message`
5. **User receives your reply** instantly!

## 📝 Bot Commands

### For Users:
- `/start` or `/help` - Welcome message
- `/order` - Display website, payment, and form links

### For Admin:
- `/r <user_id> <message>` - Reply to a specific user
  - Example: `/r 123456789 Hello! How can I help you?`

## 🔧 How It Works

1. **User sends a message** → Bot forwards it to admin with user details
2. **Admin sees**:
   ```
   📩 New Message
   
   👤 From: John Doe (@johndoe)
   🆔 User ID: 123456789
   
   💬 Message:
   Hello, I need help!
   
   Reply with: /r 123456789 your_message
   ```
3. **Admin replies**: `/r 123456789 Hi! I'm here to help.`
4. **User receives** the admin's message immediately

## 📂 Project Structure

```
fastreel-support-bot/
├── main_webhook.py      # Main bot code (webhook server)
├── requirements.txt     # Python dependencies
├── Procfile            # Railway process configuration
├── .env.example        # Environment variables template
└── README_RAILWAY.md   # This file
```

## ⚙️ Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `BOT_TOKEN` | Your Telegram bot token from @BotFather | `123456789:ABCdef...` |
| `ADMIN_ID` | Your Telegram user ID from @userinfobot | `1234567890` |
| `PUBLIC_BASE_URL` | Your Railway app URL | `https://yourapp.up.railway.app` |
| `PORT` | Server port (Railway sets this automatically) | `8080` |

## 🔄 Updating the Bot

1. Make changes to your code
2. Commit and push to GitHub (if using GitHub deployment)
   ```bash
   git add .
   git commit -m "Update bot features"
   git push
   ```
3. Railway will automatically redeploy

**OR** if using Railway CLI:
```bash
railway up
```

## 🐛 Troubleshooting

### Webhook not setting
- Check that `PUBLIC_BASE_URL` is correct (should be your Railway domain with https://)
- Ensure `BOT_TOKEN` is valid
- Check Railway logs for error messages

### Messages not forwarding
- Verify `ADMIN_ID` is correct (must be a number, not username)
- Check bot logs in Railway dashboard

### Bot not responding
- Ensure the Railway app is running (check Deployments tab)
- Verify webhook is set: send a message and check logs

## 📊 Monitoring

- **Railway Dashboard**: View logs, metrics, and deployment status
- **Health Check**: Visit `https://your-app.up.railway.app/` to see `{"status": "ok", "message": "Bot is running"}`
- **Telegram**: Message your bot to test it's responding

## 🛠️ Customization

### Change Welcome Message
Edit the `start_command` function in `main_webhook.py`:
```python
@dp.message_handler(commands=["start", "help"])
async def start_command(message: types.Message):
    await message.reply(
        "Your custom welcome message here"
    )
```

### Change Order Links
Edit the `order_command` function in `main_webhook.py`:
```python
@dp.message_handler(commands=["order"])
async def order_command(message: types.Message):
    await message.reply(
        "🧠 <b>Your Links</b>\n\n"
        "🌐 Website: https://your-website.com\n"
        "💳 Payment: https://your-payment-link\n"
        "📝 Form: https://your-form-link"
    )
```

## 🔐 Security Notes

- **Never commit `.env`** to Git - use `.env.example` instead
- Keep your `BOT_TOKEN` secret
- Use Railway's environment variables (not hardcoded values)

## 💡 Tips

1. **Test locally first** (optional):
   ```bash
   pip install -r requirements.txt
   # Create .env file with your values
   python main_webhook.py
   # Use ngrok to expose localhost for testing webhooks
   ```

2. **View Railway logs** to debug issues:
   - Go to your project → Deployments → View Logs

3. **Redeploy manually** if needed:
   - Railway Dashboard → Deployments → Redeploy

## 📞 Support

If you encounter issues:
1. Check Railway deployment logs
2. Verify all environment variables are set correctly
3. Test the webhook URL manually
4. Ensure bot token is valid with @BotFather

---

**Ready to deploy!** Follow the steps above and your bot will be live in minutes. 🚀
