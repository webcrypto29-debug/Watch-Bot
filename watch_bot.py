import logging
import uuid
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

# ----------------- CONFIGURATION -----------------
TOKEN = "8728724869:AAGEkwjkhuRjfsn0e-tqUQgowWNzB5Y4XrQ"
BOT_USERNAME = "Watch727_bot"

# Aapka GitHub Pages live hosting link
WEB_APP_URL = "https://webcrypto29-debug.github.io/Watch-Bot/" 

ADMIN_ID = 5911965767
DB_FILE = "bot_database.json"
# --------------------------------------------------

def load_db():
    if not os.path.exists(DB_FILE):
        initial_data = {
            "files": {},
            "settings": {"ad_status": True}
        }
        with open(DB_FILE, "w") as f:
            json.dump(initial_data, f)
        return initial_data
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {"files": {}, "settings": {"ad_status": True}}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user:
        return
    user_id = user.id
    args = context.args

    async def safe_reply(text, **kwargs):
        if update.message:
            return await update.message.reply_text(text, **kwargs)
        elif update.callback_query and update.callback_query.message:
            return await update.callback_query.message.reply_text(text, **kwargs)
        else:
            return await context.bot.send_message(chat_id=user_id, text=text, **kwargs)

    if args:
        param = args[0]
        db = load_db()
        file_doc = db["files"].get(param)

        if file_doc:
            target_url = file_doc.get("text", "https://google.com")
            app_url_with_param = f"{WEB_APP_URL}?url={target_url}"
            
            keyboard = [
                [InlineKeyboardButton("👀 Click Here to View Ad & Open", web_app=WebAppInfo(url=app_url_with_param))]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await safe_reply(
                "✨ **Your link is ready!**\n\nClick the button below to open the page, view the advertisement, and get redirected automatically:",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            return
        else:
            await safe_reply("❌ Invalid or expired link!")
            return

    await safe_reply(
        "👋 Welcome!\n\nSend any destination website URL to generate your smart ad-redirect link.",
        parse_mode="Markdown"
    )

async def handle_admin_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or update.effective_user.id != ADMIN_ID: return
    msg = update.message
    if not msg or not msg.text or msg.text.startswith("/"):
        return

    text_content = msg.text
    unique_id = str(uuid.uuid4())[:8]
    
    db = load_db()
    db["files"][unique_id] = {"text": text_content}
    save_db(db)

    share_link = f"https://t.me/{BOT_USERNAME}?start={unique_id}"
    await msg.reply_text(f"✅ **Ad Link Generated Successfully!**\n\n🔗 **Shareable Link:**\n`{share_link}`", parse_mode="Markdown")

if __name__ == '__main__':
    print("🚀 Starting Bot on Render...")
    app = ApplicationBuilder().token(TOKEN).connect_timeout(30.0).read_timeout(30.0).write_timeout(30.0).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_admin_content))
    
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
          
