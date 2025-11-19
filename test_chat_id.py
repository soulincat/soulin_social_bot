"""
Quick script to find your Telegram chat ID.
Run this, then send /start to your bot in Telegram.
"""
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
from dotenv import load_dotenv

load_dotenv()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"Your chat ID: {chat_id}")
    print(f"Chat ID: {chat_id}")  # Save this!

if __name__ == "__main__":
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in .env")
        exit(1)
    
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    print("🤖 Bot is running. Send /start to your bot in Telegram to get your chat ID.")
    app.run_polling()


