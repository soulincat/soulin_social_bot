"""
Send a test detailed weekly report with dummy data to Telegram
"""
import os
from dotenv import load_dotenv
from bot import send_telegram_message, format_detailed_report, get_manual_metrics, save_manual_metric, get_week_key

load_dotenv()

# Dummy data matching the sample
dummy_beehiiv = {
    'subscribers': 456,
    'open_rate': 45.2,
    'click_rate': 8.3
}

dummy_instagram = {
    'impressions': 5678,
    'reach': 3420
}

dummy_web = {
    'pageviews': 1234,
    'visitors': 1234
}

# Dummy last week data for comparison
dummy_last_week = {
    'beehiiv': {
        'subscribers': 433,
        'open_rate': 48.0,
        'click_rate': 8.5
    },
    'instagram': {
        'impressions': 5850,
        'reach': 3500
    },
    'web': {
        'pageviews': 1102,
        'visitors': 1102
    }
}

# Set up dummy manual metrics for current week
week_key = get_week_key()
save_manual_metric('linkedin_impressions', 890, week_key)
save_manual_metric('inquiries', 2, week_key)
save_manual_metric('calls_booked', 1, week_key)
save_manual_metric('retainer_signups', 1, week_key)
save_manual_metric('new_subscribers', 23, week_key)

# Get chat ID from .env
chat_id = os.getenv('TELEGRAM_CHAT_ID')

if not chat_id:
    print("❌ Error: TELEGRAM_CHAT_ID not found in .env")
    exit(1)

# Get manual metrics
manual_metrics = get_manual_metrics(week_key)

# Format detailed report
report = format_detailed_report(
    "Test Account",
    dummy_beehiiv,
    dummy_instagram,
    dummy_web,
    last_week=dummy_last_week,
    manual_metrics=manual_metrics
)

# Add test header
test_report = "🧪 **TEST - Detailed Weekly Report**\n\n" + report

print("📤 Sending detailed test report to Telegram...")
print(f"Chat ID: {chat_id}")
print("\n" + "="*50)
print("Report Preview (first 500 chars):")
print("="*50)
print(test_report[:500] + "...")
print("="*50)

# Send to Telegram
result = send_telegram_message(chat_id, test_report)

if result.get('ok'):
    print("\n✅ Detailed report sent successfully!")
    print(f"Message ID: {result.get('result', {}).get('message_id')}")
    print("\n📱 Check your Telegram for the full detailed report!")
else:
    print(f"\n❌ Error sending report: {result.get('description', 'Unknown error')}")

