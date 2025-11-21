"""
Test script to send a test report with clean formatting
"""
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from metrics_collector import collect_all_metrics
from report_formatter_dynamic import generate_full_report
from bot import send_telegram_message
from utils.projects import extract_projects

load_dotenv()

def get_test_metrics():
    """Generate test metrics"""
    return {
        'awareness': {
            'Blog': 1234,
            'Instagram': 5678,
            'LinkedIn': 890
        },
        'total_reach': 7802,
        'capture': {
            'total_subscribers': 456,
            'new_subscribers': 23,
            'open_rate': 45.2,
            'click_rate': 8.3,
            'opens': 206,
            'clicks': 38
        },
        'conversion': {
            'Inquiries': 2,
            'inquiries': 2,
            'Discovery call': 1,
            'calls_booked': 1,
            'new_clients': 1
        },
        'errors': []
    }

def send_test_report():
    """Send test report with clean formatting"""
    try:
        # Load client
        with open('clients.json', 'r') as f:
            data = json.load(f)
        
        if not data.get('clients'):
            print("❌ No clients found in clients.json")
            return
        
        client = data['clients'][0]
        chat_id = client.get('chat_id')
        
        if not chat_id:
            print("❌ No chat_id found for client")
            return
        
        # Prepare test project + metrics
        project = extract_projects(client)[0]
        metrics = get_test_metrics()
        metrics['fans_total'] = metrics['capture']['total_subscribers']
        metrics['monthly_revenue'] = 4200
        metrics['scope_id'] = project.get('scope_id')
        metrics['project_name'] = project.get('project_name')
        
        report = generate_full_report(client, project, metrics, None)
        
        # Send via Telegram
        result = send_telegram_message(chat_id, report)
        
        if result.get('ok'):
            print(f"✅ Test report sent successfully to {client.get('name', 'client')}")
            print(f"📱 Chat ID: {chat_id}")
        else:
            print(f"❌ Error sending report: {result.get('description', 'Unknown error')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 Sending test report with clean formatting...")
    send_test_report()

