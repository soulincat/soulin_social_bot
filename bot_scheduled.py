"""
Bot with scheduled weekly reports using the schedule library.
Run this file to keep the bot running and sending reports automatically.
"""
import schedule
import time
from bot import send_all_reports
from datetime import datetime

def job():
    """Job to run weekly report"""
    print(f"⏰ Running scheduled report at {datetime.now()}")
    send_all_reports()

# Run every Monday at 9 AM
schedule.every().monday.at("09:00").do(job)

# Optional: Run every day at 9 AM for testing
# schedule.every().day.at("09:00").do(job)

if __name__ == "__main__":
    print("📊 Metrics bot started...")
    print("⏰ Scheduled to run every Monday at 9:00 AM")
    print("Press Ctrl+C to stop")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


