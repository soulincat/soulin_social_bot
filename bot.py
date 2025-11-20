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

def calculate_change(current, previous):
    """Calculate percentage change and return formatted string"""
    if previous is None or previous == 0:
        return ""
    
    change = ((current - previous) / previous) * 100
    if change > 0:
        return f" (+{change:.1f}% ↗️)"
    elif change < 0:
        return f" ({change:.1f}% ↘️)"
    else:
        return " (→)"

def format_report(client_name, beehiiv, instagram, web, last_week=None):
    """Generate formatted report with optional week-over-week comparison"""
    # Calculate changes if last week's data exists
    sub_change = calculate_change(beehiiv['subscribers'], 
                                   last_week['beehiiv']['subscribers'] if last_week else None)
    open_change = calculate_change(beehiiv['open_rate'], 
                                   last_week['beehiiv']['open_rate'] if last_week else None)
    click_change = calculate_change(beehiiv['click_rate'], 
                                    last_week['beehiiv']['click_rate'] if last_week else None)
    imp_change = calculate_change(instagram['impressions'], 
                                  last_week['instagram']['impressions'] if last_week else None)
    reach_change = calculate_change(instagram['reach'], 
                                     last_week['instagram']['reach'] if last_week else None)
    pv_change = calculate_change(web['pageviews'], 
                                  last_week['web']['pageviews'] if last_week else None)
    vis_change = calculate_change(web['visitors'], 
                                  last_week['web']['visitors'] if last_week else None)
    
    message = f"""
📊 **Weekly Report: {client_name}**
_{datetime.now().strftime('%B %d, %Y')}_

📧 **Newsletter**
• Subscribers: {beehiiv['subscribers']:,}{sub_change}
• Open Rate: {beehiiv['open_rate']:.1f}%{open_change}
• Click Rate: {beehiiv['click_rate']:.1f}%{click_change}

📱 **Instagram**
• Impressions: {instagram['impressions']:,}{imp_change}
• Reach: {instagram['reach']:,}{reach_change}

🌐 **Website**
• Pageviews: {web['pageviews']:,}{pv_change}
• Visitors: {web['visitors']:,}{vis_change}

---
_Auto-generated 🤖_
"""
    return message

def format_report_with_comparison(client_name, beehiiv, instagram, web, last_week=None):
    """Alias for format_report - kept for backward compatibility"""
    return format_report(client_name, beehiiv, instagram, web, last_week)

def get_client_metrics(client):
    """Get metrics for a single client"""
    # Try to get metrics, use defaults if API keys are missing
    beehiiv = {'subscribers': 0, 'open_rate': 0, 'click_rate': 0}
    instagram = {'impressions': 0, 'reach': 0}
    web = {'pageviews': 0, 'visitors': 0}
    
    errors = []
    
    # Beehiiv
    if client.get('beehiiv_pub_id') and client['beehiiv_pub_id'] != 'your_beehiiv_pub_id':
        api_key = os.getenv('BEEHIIV_API_KEY')
        if api_key and api_key != 'your_beehiiv_api_key':
            try:
                beehiiv = get_beehiiv_metrics(client['beehiiv_pub_id'], api_key)
            except Exception as e:
                error_msg = f"⚠️ Beehiiv API error: {str(e)}"
                errors.append(error_msg)
                print(error_msg)
    
    # Instagram
    if client.get('instagram_id') and client['instagram_id'] != 'your_instagram_user_id':
        token = client.get('instagram_token') or os.getenv('INSTAGRAM_ACCESS_TOKEN')
        if token and token != 'your_instagram_access_token':
            try:
                instagram = get_instagram_metrics(client['instagram_id'], token)
            except Exception as e:
                error_msg = f"⚠️ Instagram API error: {str(e)}"
                errors.append(error_msg)
                print(error_msg)
    
    # Vercel
    if client.get('vercel_project_id') and client['vercel_project_id'] != 'your_vercel_project_id':
        token = os.getenv('VERCEL_TOKEN')
        if token and token != 'your_vercel_token':
            try:
                web = get_vercel_metrics(client['vercel_project_id'], token)
            except Exception as e:
                error_msg = f"⚠️ Vercel API error: {str(e)}"
                errors.append(error_msg)
                print(error_msg)
    
    return beehiiv, instagram, web, errors


def load_last_week_metrics(client_name):
    """Load last week's metrics from file"""
    try:
        if os.path.exists('metrics_history.json'):
            with open('metrics_history.json', 'r') as f:
                history = json.load(f)
                return history.get(client_name, None)
    except:
        pass
    return None

def save_metrics(client_name, beehiiv, instagram, web):
    """Save current metrics for next week's comparison"""
    try:
        history = {}
        if os.path.exists('metrics_history.json'):
            with open('metrics_history.json', 'r') as f:
                history = json.load(f)
        
        history[client_name] = {
            'beehiiv': beehiiv,
            'instagram': instagram,
            'web': web,
            'date': datetime.now().isoformat()
        }
        
        with open('metrics_history.json', 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"⚠️  Error saving metrics history: {e}")

def send_all_reports():
    """Send reports to all clients"""
    with open('clients.json', 'r') as f:
        data = json.load(f)
    
    for client in data['clients']:
        try:
            # Get current metrics
            beehiiv, instagram, web, errors = get_client_metrics(client)
            
            # Get last week's metrics for comparison
            last_week = load_last_week_metrics(client['name'])
            
            # Format report with comparison
            report = format_report(client['name'], beehiiv, instagram, web, last_week)
            
            # Add error alerts if any
            if errors:
                error_text = "\n\n⚠️ **API Errors:**\n" + "\n".join(f"• {e}" for e in errors)
                report += error_text
            
            send_telegram_message(client['chat_id'], report)
            
            # Save current metrics for next week's comparison
            save_metrics(client['name'], beehiiv, instagram, web)
            
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


