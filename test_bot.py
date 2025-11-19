"""
Quick test to verify the bot can send messages.
Make sure you have your chat ID in .env first!
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if not BOT_TOKEN:
    print("❌ Error: TELEGRAM_BOT_TOKEN not found in .env")
    exit(1)

if not CHAT_ID or CHAT_ID == "your_chat_id":
    print("❌ Error: Please set TELEGRAM_CHAT_ID in .env")
    print("   Run 'python test_chat_id.py' first to get your chat ID")
    exit(1)

def send_test_message():
    """Send a test message to Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': "🔥 **Bot Test**\n\nYour bot is working! ✅",
        'parse_mode': 'Markdown'
    }
    response = requests.post(url, json=payload)
    return response.json()

if __name__ == "__main__":
    print("🧪 Testing bot connection...")
    result = send_test_message()
    
    if result.get('ok'):
        print("✅ Success! Check your Telegram for the test message.")
    else:
        print(f"❌ Error: {result.get('description', 'Unknown error')}")
        print(f"Full response: {result}")

