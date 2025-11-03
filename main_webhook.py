import os
import logging
from aiohttp import web
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "")
PORT = int(os.getenv("PORT", "8080"))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is required!")
if not ADMIN_ID:
    raise ValueError("ADMIN_ID is required!")
if not PUBLIC_BASE_URL:
    raise ValueError("PUBLIC_BASE_URL is required!")

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{PUBLIC_BASE_URL}{WEBHOOK_PATH}"

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

Bot.set_current(bot)

user_sessions = {}


@dp.message_handler(commands=["start", "help"])
async def start_command(message: types.Message):
    """Welcome message for users"""
    await bot.send_message(
        message.chat.id,
        "👋 <b>Welcome to FastReel AI Support!</b>\n\n"
        "Send your question or request here — I'll reply as soon as possible.\n\n"
        "Use /order to view our main links."
    )


@dp.message_handler(commands=["order"])
async def order_command(message: types.Message):
    """Display order links"""
    await bot.send_message(
        message.chat.id,
        "🧠 <b>Order Links</b>\n\n"
        "🌐 Website: https://fastreelai.framer.website/\n"
        "💳 Payment: https://misapasta.gumroad.com/l/dfokn\n"
        "📝 Form: https://forms.gle/FsRqWmLsBZYnjWCk9"
    )


@dp.message_handler(lambda msg: msg.from_user.id == ADMIN_ID, commands=["r"])
async def admin_reply_command(message: types.Message):
    """Admin replies to a user using /r <user_id> <text>"""
    try:
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            await bot.send_message(
                message.chat.id,
                "❌ Usage: /r <user_id> <message>\n"
                "Example: /r 123456789 Hello, how can I help you?"
            )
            return
        
        user_id = int(parts[1])
        reply_text = parts[2]
        
        await bot.send_message(user_id, reply_text)
        await bot.send_message(message.chat.id, f"✅ Message sent to user {user_id}")
        logger.info(f"Admin sent message to user {user_id}")
        
    except ValueError:
        await bot.send_message(message.chat.id, "❌ Invalid user ID. Must be a number.")
    except Exception as e:
        logger.error(f"Error sending message to user: {e}")
        await bot.send_message(message.chat.id, f"❌ Error: {e}")


@dp.message_handler(content_types=types.ContentTypes.ANY)
async def forward_to_admin(message: types.Message):
    """Forward all user messages to admin"""
    if message.from_user.id == ADMIN_ID:
        return
    
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    username = f"@{message.from_user.username}" if message.from_user.username else "No username"
    
    user_sessions[user_id] = {
        "name": user_name,
        "username": username
    }
    
    try:
        if message.content_type == "text":
            forward_text = (
                f"📩 <b>New Message</b>\n\n"
                f"👤 From: {user_name} ({username})\n"
                f"🆔 User ID: <code>{user_id}</code>\n\n"
                f"💬 Message:\n{message.text}\n\n"
                f"Reply with: <code>/r {user_id} your_message</code>"
            )
            await bot.send_message(ADMIN_ID, forward_text)
        else:
            content_type_str = message.content_type if message.content_type else "MEDIA"
            caption = (
                f"📩 <b>New {content_type_str.upper()}</b>\n\n"
                f"👤 From: {user_name} ({username})\n"
                f"🆔 User ID: <code>{user_id}</code>\n\n"
                f"Reply with: <code>/r {user_id} your_message</code>"
            )
            await message.copy_to(ADMIN_ID, caption=caption)
        
        await bot.send_message(message.chat.id, "✅ Your message has been received! I'll get back to you soon.")
        logger.info(f"Forwarded message from user {user_id} ({user_name}) to admin")
    except Exception as e:
        logger.error(f"Error forwarding message to admin: {e}")
        await bot.send_message(message.chat.id, "⚠️ An error occurred. Please try again later.")


async def on_startup(app):
    """Set webhook on startup"""
    webhook_info = await bot.get_webhook_info()
    
    if webhook_info.url != WEBHOOK_URL:
        logger.info("Deleting old webhook...")
        await bot.delete_webhook()
        logger.info(f"Setting new webhook: {WEBHOOK_URL}")
        await bot.set_webhook(WEBHOOK_URL)
        logger.info("✅ Webhook successfully set!")
    else:
        logger.info(f"✅ Webhook already set to: {WEBHOOK_URL}")


async def on_shutdown(app):
    """Clean up on shutdown"""
    logger.info("Shutting down...")
    await bot.delete_webhook()
    if dp.storage:
        await dp.storage.close()
        await dp.storage.wait_closed()
    if bot.session:
        await bot.session.close()


async def webhook_handler(request):
    """Handle incoming webhook updates from Telegram"""
    if request.match_info.get("token") == BOT_TOKEN:
        update = types.Update(**(await request.json()))
        await dp.process_update(update)
        return web.Response()
    else:
        return web.Response(status=403)


async def health_check(request):
    """Health check endpoint"""
    return web.json_response({"status": "ok", "message": "Bot is running"})


if __name__ == "__main__":
    app = web.Application()
    app.router.add_post("/webhook/{token}", webhook_handler)
    app.router.add_get("/", health_check)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    
    logger.info(f"Starting webhook server on port {PORT}")
    logger.info(f"Webhook URL: {WEBHOOK_URL}")
    
    web.run_app(app, host="0.0.0.0", port=PORT)
