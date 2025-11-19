#!/usr/bin/env python3
"""Verify bot setup and send a test message"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

print("=" * 50)
print("Bot Setup Verification")
print("=" * 50)
print(f"Bot Token: {'✅ Set' if BOT_TOKEN and BOT_TOKEN != 'your_bot_token_here' else '❌ Missing'}")
print(f"Chat ID: {CHAT_ID if CHAT_ID and CHAT_ID != 'your_chat_id' else '❌ Missing'}")

if not BOT_TOKEN or BOT_TOKEN == 'your_bot_token_here':
    print("\n❌ Please set TELEGRAM_BOT_TOKEN in .env")
    exit(1)

if not CHAT_ID or CHAT_ID == 'your_chat_id':
    print("\n❌ Please set TELEGRAM_CHAT_ID in .env")
    exit(1)

print("\n🧪 Sending test message...")
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {
    'chat_id': CHAT_ID,
    'text': "🔥 **Bot Test**\n\nYour bot is working! ✅\n\nChat ID: " + str(CHAT_ID),
    'parse_mode': 'Markdown'
}

try:
    response = requests.post(url, json=payload, timeout=10)
    result = response.json()
    
    if result.get('ok'):
        print("✅ SUCCESS! Check your Telegram for the test message.")
        print(f"   Message ID: {result.get('result', {}).get('message_id')}")
    else:
        print(f"❌ Error: {result.get('description', 'Unknown error')}")
        print(f"   Full response: {result}")
except Exception as e:
    print(f"❌ Exception: {e}")

print("=" * 50)

