"""
Simple cron-compatible script for weekly Telegram reports
Run this with a cron job or task scheduler
Usage: python cron_weekly.py
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import bot functions
from bot import send_all_reports

def main():
    """Main function to send weekly reports"""
    print(f"⏰ Running weekly report at {datetime.now()}")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if bot token is set
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in environment")
        print("   Please set it in .env file or environment variables")
        sys.exit(1)
    
    try:
        # Send all reports with detailed format
        print("📊 Generating and sending weekly reports...")
        send_all_reports(use_detailed=True)
        print("✅ Weekly reports sent successfully!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error sending reports: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

