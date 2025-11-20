"""
Interactive bot with /metrics command for on-demand reports
Run this to enable Telegram commands
"""
import os
import json
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
from bot import (
    format_report_with_comparison,
    save_metrics,
    get_client_metrics,
    load_last_week_metrics
)

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

async def metrics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /metrics command - send on-demand report"""
    chat_id = str(update.effective_chat.id)
    
    # Find client by chat_id
    try:
        with open('clients.json', 'r') as f:
            clients_data = json.load(f)
        
        client = None
        for c in clients_data['clients']:
            if str(c['chat_id']) == chat_id:
                client = c
                break
        
        if not client:
            await update.message.reply_text(
                "❌ Your chat ID is not configured in clients.json. "
                "Please add your chat ID to the clients list."
            )
            return
        
        # Get current metrics
        beehiiv, instagram, web, errors = get_client_metrics(client)
        
        # Get last week's metrics for comparison
        last_week = load_last_week_metrics(client['name'])
        
        # Format report with comparison
        report = format_report_with_comparison(
            client['name'], 
            beehiiv, 
            instagram, 
            web,
            last_week
        )
        
        # Add error alerts if any
        if errors:
            error_text = "\n\n⚠️ **API Errors:**\n" + "\n".join(f"• {e}" for e in errors)
            report += error_text
        
        await update.message.reply_text(report, parse_mode='Markdown')
        
        # Save current metrics for next week's comparison
        save_metrics(client['name'], beehiiv, instagram, web)
        
    except Exception as e:
        error_msg = f"❌ Error generating report: {str(e)}"
        await update.message.reply_text(error_msg)
        print(f"Error in /metrics command: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "🤖 **Metrics Bot**\n\n"
        "Commands:\n"
        "• `/metrics` - Get your weekly metrics report\n"
        "• `/start` - Show this help message\n\n"
        "The bot will also send automated weekly reports every Monday at 9 AM.",
        parse_mode='Markdown'
    )

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in .env")
        exit(1)
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("metrics", metrics))
    
    print("🤖 Interactive bot started...")
    print("📱 Commands available:")
    print("   /start - Show help")
    print("   /metrics - Get on-demand report")
    print("\nPress Ctrl+C to stop")
    
    app.run_polling()

