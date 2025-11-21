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
    load_last_week_metrics,
    get_manual_metrics,
    save_manual_metric,
    get_week_key
)
from metrics_collector import (
    collect_all_metrics,
    save_manual_metric as save_manual_metric_new,
    get_manual_metrics_list,
    is_valid_metric
)
from report_formatter_dynamic import generate_full_report
from utils.projects import extract_projects

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEB_DASHBOARD_URL = os.getenv('WEB_DASHBOARD_URL', 'https://yourapp.com/dashboard')

def format_quick_summary(project, metrics):
    """Compose a short metrics summary block."""
    capture = metrics.get('capture', {})
    summary = [
        f"📍 {project.get('project_name', 'Project')}",
        f"👀 Reach: {metrics.get('total_reach', 0):,}",
        f"🧲 New subs: {capture.get('new_subscribers', 0):,}",
        f"💌 Opens: {capture.get('open_rate', 0):.1f}%  | Clicks: {capture.get('click_rate', 0):.1f}%",
        f"🎯 Inquiries: {metrics.get('inquiries', 0)}  | Calls: {metrics.get('calls_booked', 0)}",
        f"💰 Clients: {metrics.get('new_clients', 0)}  | Fans: {metrics.get('fans_total', capture.get('total_subscribers', 0)):,}",
    ]
    return "\n".join(summary)


async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /report command - send full weekly report + dashboard link"""
    chat_id = str(update.effective_chat.id)
    
    try:
        client = get_client_by_chat_id(chat_id)
        if not client:
            await update.message.reply_text(
                "❌ Your chat ID is not configured in clients.json. "
                "Please add your chat ID to the clients list."
            )
            return
        
        projects = extract_projects(client)
        if not projects:
            await update.message.reply_text("❌ No projects configured yet. Please complete onboarding.")
            return
        
        from scheduler import load_last_period_metrics
        
        for project in projects:
            metrics_data = collect_all_metrics(client, project)
            scope_id = metrics_data.get('scope_id')
            last_week = load_last_period_metrics(scope_id)
            report_text = generate_full_report(client, project, metrics_data, last_week)
            dashboard_link = f"\n\n🔗 View dashboard: {WEB_DASHBOARD_URL}?project={project.get('project_id', scope_id)}"
            await update.message.reply_text(report_text + dashboard_link, parse_mode='Markdown')
        
    except Exception as e:
        error_msg = f"❌ Error generating report: {str(e)}"
        await update.message.reply_text(error_msg)
        print(f"Error in /report command: {e}")

async def metrics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /metrics command - send quick metrics summary"""
    chat_id = str(update.effective_chat.id)
    
    try:
        client = get_client_by_chat_id(chat_id)
        
        if not client:
            await update.message.reply_text(
                "❌ Your chat ID is not configured in clients.json. "
                "Please add your chat ID to the clients list."
            )
            return
        
        projects = extract_projects(client)
        if not projects:
            await update.message.reply_text("❌ No projects configured yet. Please complete onboarding.")
            return
        
        summaries = []
        for project in projects:
            metrics_data = collect_all_metrics(client, project)
            summaries.append(format_quick_summary(project, metrics_data))
        
        summary_text = "\n\n".join(summaries)
        await update.message.reply_text(summary_text, parse_mode='Markdown')
        
    except Exception as e:
        error_msg = f"❌ Error generating report: {str(e)}"
        await update.message.reply_text(error_msg)
        print(f"Error in /metrics command: {e}")

def get_client_by_chat_id(chat_id):
    """Get client data by chat_id"""
    try:
        with open('clients.json', 'r') as f:
            clients_data = json.load(f)
        
        for c in clients_data['clients']:
            if str(c.get('chat_id')) == str(chat_id):
                return c
    except:
        pass
    return None

async def update_metric(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /update command - update manual metrics (dynamic based on client config)"""
    chat_id = str(update.effective_chat.id)
    
    # Get client
    client = get_client_by_chat_id(chat_id)
    if not client:
        await update.message.reply_text("❌ Client not found. Please contact support.")
        return
    
    client_id = client.get('client_id', 'unknown')
    projects = extract_projects(client)
    project = projects[0] if projects else {'scope_id': client_id}
    scope_id = project.get('scope_id', client_id)
    
    # Parse command
    if not context.args or len(context.args) < 2:
        # Show available metrics for this client
        available = get_manual_metrics_list(client, project)
        if available:
            msg = f"Usage: `/update [metric] [value]`\n\n*Your metrics:*\n{chr(10).join(available)}"
        else:
            msg = "Usage: `/update [metric] [value]`\n\nNo manual metrics configured for your funnel."
        await update.message.reply_text(msg, parse_mode='Markdown')
        return
    
    metric_name = context.args[0]
    try:
        value = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ Value must be a number")
        return
    
    # Validate metric exists in client's funnel
    if not is_valid_metric(client, metric_name, project):
        await update.message.reply_text(
            f"❌ Unknown metric: {metric_name}\n\nUse `/update` to see available metrics.",
            parse_mode='Markdown'
        )
        return
    
    # Save to manual_metrics.json
    success = save_manual_metric_new(scope_id, metric_name, value)
    
    if success:
        await update.message.reply_text(f"✅ Updated {metric_name} = {value}")
    else:
        await update.message.reply_text(f"❌ Error: Could not save metric")

async def funnel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /funnel command - alias for quick metrics summary"""
    await metrics(update, context)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current setup status"""
    chat_id = str(update.effective_chat.id)
    client = get_client_by_chat_id(chat_id)
    
    if not client:
        await update.message.reply_text("❌ Not found")
        return
    
    # Check connection status
    funnel = client.get('funnel_structure', {})
    settings = client.get('report_settings', {})
    
    status_msg = f"""
📊 *YOUR STATUS*

*Funnel:*
👀 {len(funnel.get('awareness', {}).get('channels', []))} awareness channels
🧲 {funnel.get('capture', {}).get('platform', 'N/A')}
💌 {funnel.get('nurture', {}).get('frequency', 'N/A')} emails
🎯 {len(funnel.get('conversion', {}).get('touchpoints', []))} conversion methods
💰 {len(funnel.get('products', []))} products

*Reports:*
Frequency: {settings.get('frequency', 'weekly')}
Day: {settings.get('day', 'Monday')}
Time: {settings.get('time', '09:00')}

*Commands:*
/update - Log metrics
/help - All commands
"""
    
    await update.message.reply_text(status_msg, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all available commands"""
    help_text = """
🤖 *COMMANDS*

*Metrics:*
/update [metric] [value] - Log manual metrics
Example: /update inquiries 3

*Status:*
/status - Your current setup
/nextreport - When is next report

*Reports:*
/report - Generate quick report now
/metrics - Generate detailed report now

*Help:*
/help - This message
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "🤖 **Metrics Bot - Funnel Dashboard**\n\n"
        "Commands:\n"
        "• `/report` - Quick simple metrics (fast)\n"
        "• `/metrics` or `/funnel` - Detailed report with insights\n"
        "• `/update <metric> <value>` - Update manual metrics\n"
        "• `/status` - Your current setup\n"
        "• `/help` - All commands\n"
        "• `/start` - Show this help message\n\n"
        "The bot sends detailed weekly reports automatically based on your settings.",
        parse_mode='Markdown'
    )

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in .env")
        exit(1)
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("metrics", metrics))
    app.add_handler(CommandHandler("funnel", funnel))
    app.add_handler(CommandHandler("update", update_metric))
    
    print("🤖 Interactive bot started...")
    print("📱 Commands available:")
    print("   /start - Show help")
    print("   /report - Quick simple metrics")
    print("   /metrics or /funnel - Detailed report with insights")
    print("   /update <metric> <value> - Update manual metrics")
    print("\nPress Ctrl+C to stop")
    
    app.run_polling()

