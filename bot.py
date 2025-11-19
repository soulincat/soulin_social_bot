import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

def send_telegram_message(chat_id, message):
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    response = requests.post(url, json=payload)
    return response.json()

def get_beehiiv_metrics(pub_id, api_key):
    """Fetch newsletter metrics from Beehiiv"""
    url = f"https://api.beehiiv.com/v2/publications/{pub_id}/stats"
    headers = {'Authorization': f'Bearer {api_key}'}
    response = requests.get(url, headers=headers)
    data = response.json()
    return {
        'subscribers': data.get('total_subscribers', 0),
        'open_rate': data.get('avg_open_rate', 0),
        'click_rate': data.get('avg_click_rate', 0)
    }

def get_instagram_metrics(user_id, access_token):
    """Fetch IG insights"""
    metrics = 'impressions,reach'
    since = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    until = datetime.now().strftime('%Y-%m-%d')
    
    url = f"https://graph.facebook.com/v18.0/{user_id}/insights"
    params = {
        'metric': metrics,
        'period': 'day',
        'since': since,
        'until': until,
        'access_token': access_token
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    impressions = sum([d['values'][0]['value'] for d in data['data'] if d['name'] == 'impressions'])
    reach = sum([d['values'][0]['value'] for d in data['data'] if d['name'] == 'reach'])
    
    return {'impressions': impressions, 'reach': reach}

def get_vercel_metrics(project_id, token):
    """Fetch web analytics from Vercel"""
    url = f"https://api.vercel.com/v1/projects/{project_id}/analytics"
    headers = {'Authorization': f'Bearer {token}'}
    params = {
        'from': int((datetime.now() - timedelta(days=7)).timestamp() * 1000),
        'to': int(datetime.now().timestamp() * 1000)
    }
    
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    
    return {
        'pageviews': data.get('pageviews', 0),
        'visitors': data.get('visitors', 0)
    }

def format_report(client_name, beehiiv, instagram, web):
    """Generate formatted report"""
    message = f"""
📊 **Weekly Report: {client_name}**
_{datetime.now().strftime('%B %d, %Y')}_

📧 **Newsletter**
• Subscribers: {beehiiv['subscribers']:,}
• Open Rate: {beehiiv['open_rate']:.1f}%
• Click Rate: {beehiiv['click_rate']:.1f}%

📱 **Instagram**
• Impressions: {instagram['impressions']:,}
• Reach: {instagram['reach']:,}

🌐 **Website**
• Pageviews: {web['pageviews']:,}
• Visitors: {web['visitors']:,}

---
_Auto-generated 🤖_
"""
    return message

def send_all_reports():
    """Send reports to all clients"""
    with open('clients.json', 'r') as f:
        data = json.load(f)
    
    for client in data['clients']:
        try:
            # Try to get metrics, use defaults if API keys are missing
            beehiiv = {'subscribers': 0, 'open_rate': 0, 'click_rate': 0}
            instagram = {'impressions': 0, 'reach': 0}
            web = {'pageviews': 0, 'visitors': 0}
            
            # Beehiiv
            if client.get('beehiiv_pub_id') and client['beehiiv_pub_id'] != 'your_beehiiv_pub_id':
                api_key = os.getenv('BEEHIIV_API_KEY')
                if api_key and api_key != 'your_beehiiv_api_key':
                    try:
                        beehiiv = get_beehiiv_metrics(client['beehiiv_pub_id'], api_key)
                    except Exception as e:
                        print(f"⚠️  Beehiiv error for {client['name']}: {e}")
            
            # Instagram
            if client.get('instagram_id') and client['instagram_id'] != 'your_instagram_user_id':
                token = client.get('instagram_token') or os.getenv('INSTAGRAM_ACCESS_TOKEN')
                if token and token != 'your_instagram_access_token':
                    try:
                        instagram = get_instagram_metrics(client['instagram_id'], token)
                    except Exception as e:
                        print(f"⚠️  Instagram error for {client['name']}: {e}")
            
            # Vercel
            if client.get('vercel_project_id') and client['vercel_project_id'] != 'your_vercel_project_id':
                token = os.getenv('VERCEL_TOKEN')
                if token and token != 'your_vercel_token':
                    try:
                        web = get_vercel_metrics(client['vercel_project_id'], token)
                    except Exception as e:
                        print(f"⚠️  Vercel error for {client['name']}: {e}")
            
            report = format_report(client['name'], beehiiv, instagram, web)
            send_telegram_message(client['chat_id'], report)
            
            print(f"✅ Sent to {client['name']}")
            
        except Exception as e:
            error = f"❌ Error for {client['name']}: {str(e)}"
            print(error)
            try:
                send_telegram_message(client['chat_id'], error)
            except:
                pass

if __name__ == "__main__":
    send_all_reports()


