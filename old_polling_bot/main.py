import os, time, csv, re, datetime as dt
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keep_alive import keep_alive

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID  = int(os.getenv("ADMIN_ID", "0"))

assert BOT_TOKEN and ADMIN_ID, "Set BOT_TOKEN and ADMIN_ID in Replit Secrets."

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp  = Dispatcher(bot)

# ---------- state ----------
last_ts = {}                 # anti-spam per user
last_seen_day = {}           # user_id -> yyyymmdd (for NEW badge)
CURRENT_TARGET = None        # active recipient for admin session
LOG = "dialog_log.csv"

# closing text sent to user when admin runs /end
CLOSING_TEXT = "Thank you for reaching out! If you have more questions, just message me here anytime."

# ---------- logging ----------
if not os.path.exists(LOG):
    with open(LOG, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["epoch","direction","user_id","name","type","text"])

def log(direction, user_id, name, msg_type, text=""):
    with open(LOG, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([int(time.time()), direction, user_id, name or "", msg_type, text])

def today_key():
    return int(dt.datetime.utcnow().strftime("%Y%m%d"))

def admin_card(uid: int, name: str):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("Answer (set target)", callback_data=f"ans:{uid}"),
        InlineKeyboardButton("Open chat", url=f"tg://user?id={uid}")
    )
    kb.add(
        InlineKeyboardButton("Quick: Thanks", callback_data=f"qr:thanks:{uid}"),
        InlineKeyboardButton("Quick: On it",  callback_data=f"qr:onit:{uid}")
    )
    return kb

# ---------- public commands ----------
@dp.message_handler(commands=["start","help"])
async def cmd_start(m: types.Message):
    await m.reply(
        "👋 <b>Welcome to FastReel AI Support!</b>\n\n"
        "Send your message here — I’ll reply as soon as possible.\n"
        "Use /order to view our main links."
    )

@dp.message_handler(commands=["order"])
async def cmd_order(m: types.Message):
    await m.reply(
        "🧠 <b>Order Links</b>\n\n"
        "🌐 Website: https://your-framer-site\n"
        "💳 Payment: https://your-pay-link\n"
        "📝 Form: https://your-google-form"
    )

# ---------- admin-only utilities ----------
def admin_only(func):
    async def wrapper(m: types.Message, *a, **kw):
        if m.from_user.id != ADMIN_ID:
            return
        return await func(m, *a, **kw)
    return wrapper

@dp.message_handler(commands=["who"])
@admin_only
async def cmd_who(m: types.Message):
    global CURRENT_TARGET
    if CURRENT_TARGET:
        await m.reply(f"🎯 Current target: <code>{CURRENT_TARGET}</code>\nSend any message/media to deliver it.\nUse /end to finish the session.")
    else:
        await m.reply("No active target. Use /answer <user_id> or tap “Answer (set target)” under a notification card.")

@dp.message_handler(commands=["answer"])
@admin_only
async def cmd_answer(m: types.Message):
    """Set active recipient: /answer <user_id>"""
    global CURRENT_TARGET
    args = m.get_args().strip()
    if not args or not args.isdigit():
        await m.reply("Usage: /answer <user_id>\nTip: the user_id is shown in the admin notification card.")
        return
    CURRENT_TARGET = int(args)
    await m.reply(
        f"✅ Target set to <code>{CURRENT_TARGET}</code>.\n"
        "Send any message (text/photo/video/file/voice) — it will be delivered to this user.\n"
        "Use /end to finish the session and send a closing message."
    )

@dp.message_handler(commands=["end"])
@admin_only
async def cmd_end(m: types.Message):
    """Finish session and send closing message to the current target"""
    global CURRENT_TARGET
    if not CURRENT_TARGET:
        await m.reply("No active target to end. Use /answer <user_id> first.")
        return
    try:
        await bot.send_message(CURRENT_TARGET, CLOSING_TEXT)
        log("out", CURRENT_TARGET, "admin", "text", CLOSING_TEXT)
        await m.reply(f"🧹 Session ended and closing message sent to <code>{CURRENT_TARGET}</code>.")
    except Exception as e:
        await m.reply(f"❌ Failed to send closing message: {e}")
    finally:
        CURRENT_TARGET = None

# Optional: quick direct command /r <user_id> <text>
@dp.message_handler(commands=["r"])
@admin_only
async def cmd_reply_direct(m: types.Message):
    args = m.get_args()
    if not args:
        await m.reply("Usage: /r <user_id> <text>")
        return
    mt = re.match(r"(\d{5,})\s+(.+)", args, flags=re.S)
    if not mt:
        await m.reply("Usage: /r <user_id> <text>")
        return
    uid = int(mt.group(1)); text = mt.group(2).strip()
    try:
        await bot.send_message(uid, text)
        log("out", uid, "admin", "text", text)
        await m.reply(f"✅ Delivered to <code>{uid}</code>.")
    except Exception as e:
        await m.reply(f"❌ Failed: {e}")

# ---------- callbacks for admin cards ----------
@dp.callback_query_handler(lambda c: c.data.startswith("ans:"))
async def cb_answer(c: types.CallbackQuery):
    global CURRENT_TARGET
    if c.from_user.id != ADMIN_ID:
        await c.answer("Admin only.", show_alert=True); return
    uid = int(c.data.split(":")[1])
    CURRENT_TARGET = uid
    await c.answer("Target set")
    await c.message.reply(
        f"✅ Target set to <code>{uid}</code>.\n"
        "Send your message now. Use /end to finish the session."
    )

@dp.callback_query_handler(lambda c: c.data.startswith("qr:"))
async def cb_quick(c: types.CallbackQuery):
    if c.from_user.id != ADMIN_ID:
        await c.answer("Admin only.", show_alert=True); return
    _, kind, uid_str = c.data.split(":")
    uid = int(uid_str)
    try:
        if kind == "thanks":
            msg = "Thanks! I’ve received your message and will get back to you shortly."
        elif kind == "onit":
            msg = "Got it — I’m on it now. I’ll update you soon."
        else:
            msg = "Thanks for your message!"
        await bot.send_message(uid, msg)
        await c.answer("Sent ✅")
    except Exception as e:
        await c.answer(f"Failed: {e}", show_alert=True)

# ---------- inbound routing ----------
@dp.message_handler(content_types=types.ContentTypes.ANY)
async def router(m: types.Message):
    global CURRENT_TARGET
    # If admin is talking and session is active -> forward to CURRENT_TARGET
    if m.from_user.id == ADMIN_ID and CURRENT_TARGET:
        try:
            if m.content_type == "text":
                await bot.send_message(CURRENT_TARGET, m.text)
                log("out", CURRENT_TARGET, "admin", "text", m.text)
            else:
                await m.copy_to(CURRENT_TARGET)
                log("out", CURRENT_TARGET, "admin", m.content_type)
            await m.reply("✅ Sent to current target.")
        except Exception as e:
            await m.reply(f"❌ Failed: {e}")
        return

    # Regular user message → notify admin
    if m.from_user.id != ADMIN_ID:
        now = time.time()
        if now - last_ts.get(m.from_user.id, 0) < 1:
            return
        last_ts[m.from_user.id] = now

        name = m.from_user.full_name
        uid  = m.from_user.id

        tkey = today_key()
        is_new = last_seen_day.get(uid) != tkey
        last_seen_day[uid] = tkey
        badge = " 🔴 <b>NEW</b>" if is_new else ""

        if m.content_type == "text":
            header = (
                f"🚨 <b>New client message</b>{badge}\n"
                f"👤 <b>{name}</b> (<code>{uid}</code>)\n\n{m.text}"
            )
            await bot.send_message(ADMIN_ID, header, reply_markup=admin_card(uid, name))
            log("in", uid, name, "text", m.text)
        else:
            header = (
                f"🚨 <b>New client message</b>{badge}\n"
                f"👤 <b>{name}</b> (<code>{uid}</code>) sent <b>{m.content_type}</b>"
            )
            await bot.send_message(ADMIN_ID, header, reply_markup=admin_card(uid, name))
            await m.copy_to(ADMIN_ID)
            log("in", uid, name, m.content_type)

        await m.reply("✅ Your message has been received! I’ll get back to you soon.")

if __name__ == "__main__":
    keep_alive()
    executor.start_polling(dp, skip_updates=True)
