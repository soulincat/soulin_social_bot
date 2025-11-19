"""
Test mode bot - works without API keys, shows sample data
Use this to see how the reports will look!
"""
import os
import json
from datetime import datetime
from bot import send_telegram_message, format_report

def get_mock_metrics():
    """Return mock metrics for testing"""
    return {
        'beehiiv': {
            'subscribers': 1250,
            'open_rate': 42.5,
            'click_rate': 8.3
        },
        'instagram': {
            'impressions': 15420,
            'reach': 8920
        },
        'web': {
            'pageviews': 3420,
            'visitors': 1890
        }
    }

def send_test_report():
    """Send a test report with mock data"""
    with open('clients.json', 'r') as f:
        data = json.load(f)
    
    mock = get_mock_metrics()
    
    for client in data['clients']:
        try:
            report = format_report(
                client['name'] + " (TEST MODE)",
                mock['beehiiv'],
                mock['instagram'],
                mock['web']
            )
            
            # Add a note that this is test data
            report = "🧪 **TEST MODE - Sample Data**\n\n" + report
            
            send_telegram_message(client['chat_id'], report)
            print(f"✅ Sent test report to {client['name']}")
            
        except Exception as e:
            error = f"❌ Error for {client['name']}: {str(e)}"
            print(error)

if __name__ == "__main__":
    print("🧪 Running in TEST MODE with sample data...")
    send_test_report()
    print("\n✅ Check your Telegram for the test report!")

