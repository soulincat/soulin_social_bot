import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

def send_telegram_message(chat_id, message):
    """Send message to Telegram (splits if too long)"""
    # Telegram limit is 4096 characters
    max_length = 4000  # Leave some buffer
    
    if len(message) <= max_length:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }
        response = requests.post(url, json=payload)
        return response.json()
    else:
        # Split into multiple messages
        parts = []
        lines = message.split('\n')
        current_part = ""
        
        for line in lines:
            if len(current_part) + len(line) + 1 > max_length:
                if current_part:
                    parts.append(current_part)
                current_part = line + '\n'
            else:
                current_part += line + '\n'
        
        if current_part:
            parts.append(current_part)
        
        # Send all parts
        results = []
        for i, part in enumerate(parts):
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': part,
                'parse_mode': 'Markdown'
            }
            if i > 0:
                # Add continuation header
                payload['text'] = f"_(Part {i+1}/{len(parts)})_\n\n" + part
            response = requests.post(url, json=payload)
            results.append(response.json())
            # Small delay between messages
            import time
            time.sleep(0.5)
        
        return results[0] if results else {'ok': False, 'description': 'Failed to send'}

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

def get_instagram_profile(user_id, access_token):
    """Fetch IG profile info (followers, profile pic, bio)"""
    try:
        url = f"https://graph.facebook.com/v18.0/{user_id}"
        params = {
            'fields': 'username,biography,profile_picture_url,followers_count',
            'access_token': access_token
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error fetching Instagram profile: {e}")
        return None

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

def calculate_conversion_rates(funnel_data):
    """Calculate conversion rates between funnel stages"""
    rates = {}
    
    # Blog → Email conversion rate
    blog_visitors = funnel_data.get('awareness', {}).get('blog_visitors', 0)
    new_subscribers = funnel_data.get('lead_capture', {}).get('new_subscribers', 0)
    if blog_visitors > 0:
        rates['blog_to_email'] = (new_subscribers / blog_visitors) * 100
    else:
        rates['blog_to_email'] = 0
    
    # Email → Inquiry conversion rate
    total_subscribers = funnel_data.get('lead_capture', {}).get('total_subscribers', 0)
    inquiries = funnel_data.get('conversion', {}).get('inquiries', 0)
    if total_subscribers > 0:
        rates['email_to_inquiry'] = (inquiries / total_subscribers) * 100
    else:
        rates['email_to_inquiry'] = 0
    
    # Inquiry → Call conversion rate
    calls_booked = funnel_data.get('conversion', {}).get('calls_booked', 0)
    if inquiries > 0:
        rates['inquiry_to_call'] = (calls_booked / inquiries) * 100
    else:
        rates['inquiry_to_call'] = 0
    
    # Call → Client conversion rate
    retainer_signups = funnel_data.get('conversion', {}).get('retainer_signups', 0)
    if calls_booked > 0:
        rates['call_to_client'] = (retainer_signups / calls_booked) * 100
    else:
        rates['call_to_client'] = 0
    
    return rates

def get_funnel_metrics(beehiiv, instagram, web, manual_metrics, last_week=None):
    """Aggregate all metrics into funnel structure"""
    # Calculate new subscribers (this week vs last week)
    # If manual entry exists, use it; otherwise calculate from last week
    new_subscribers = manual_metrics.get('new_subscribers', 0)
    if new_subscribers == 0 and last_week:
        current_subs = beehiiv.get('subscribers', 0)
        last_subs = last_week.get('beehiiv', {}).get('subscribers', 0)
        new_subscribers = max(0, current_subs - last_subs)
    
    funnel = {
        'awareness': {
            'blog_visitors': web.get('visitors', 0),
            'blog_pageviews': web.get('pageviews', 0),
            'instagram_impressions': instagram.get('impressions', 0),
            'instagram_reach': instagram.get('reach', 0),
            'linkedin_impressions': manual_metrics.get('linkedin_impressions', 0)
        },
        'lead_capture': {
            'new_subscribers': new_subscribers,
            'total_subscribers': beehiiv.get('subscribers', 0),
            'conversion_rate': 0  # Will be calculated
        },
        'nurture': {
            'open_rate': beehiiv.get('open_rate', 0),
            'click_rate': beehiiv.get('click_rate', 0)
        },
        'conversion': {
            'inquiries': manual_metrics.get('inquiries', 0),
            'calls_booked': manual_metrics.get('calls_booked', 0),
            'retainer_signups': manual_metrics.get('retainer_signups', 0)
        }
    }
    
    # Calculate conversion rates
    conversion_rates = calculate_conversion_rates(funnel)
    funnel['lead_capture']['conversion_rate'] = conversion_rates.get('blog_to_email', 0)
    funnel['conversion']['email_to_inquiry_rate'] = conversion_rates.get('email_to_inquiry', 0)
    funnel['conversion']['inquiry_to_call_rate'] = conversion_rates.get('inquiry_to_call', 0)
    funnel['conversion']['call_to_client_rate'] = conversion_rates.get('call_to_client', 0)
    
    return funnel

def format_report(client_name, beehiiv, instagram, web, last_week=None, manual_metrics=None):
    """Generate formatted funnel report"""
    if manual_metrics is None:
        manual_metrics = get_manual_metrics()
    
    # Get funnel structure
    funnel = get_funnel_metrics(beehiiv, instagram, web, manual_metrics, last_week)
    
    # Get date range for the week
    today = datetime.now()
    days_since_monday = today.weekday()
    monday = today - timedelta(days=days_since_monday)
    week_start = monday.strftime('%b %d')
    week_end = (monday + timedelta(days=6)).strftime('%b %d, %Y')
    
    message = f"""
📊 **Weekly Funnel Report: {client_name}**
_{week_start} - {week_end}_

🎯 **AWARENESS**
• Blog: {funnel['awareness']['blog_visitors']:,} visitors
• Instagram: {funnel['awareness']['instagram_impressions']:,} impressions
• LinkedIn: {funnel['awareness']['linkedin_impressions']:,} impressions

🧲 **LEAD CAPTURE**
• New subscribers: {funnel['lead_capture']['new_subscribers']:,}
• Total subscribers: {funnel['lead_capture']['total_subscribers']:,}
• Conversion rate: {funnel['lead_capture']['conversion_rate']:.1f}%

💌 **NURTURE**
• Newsletter open: {funnel['nurture']['open_rate']:.1f}%
• Click rate: {funnel['nurture']['click_rate']:.1f}%

💰 **CONVERSION**
• Inquiries: {funnel['conversion']['inquiries']:,}
• Calls booked: {funnel['conversion']['calls_booked']:,}
• New clients: {funnel['conversion']['retainer_signups']:,}
• Email→Inquiry: {funnel['conversion']['email_to_inquiry_rate']:.1f}%
• Inquiry→Call: {funnel['conversion']['inquiry_to_call_rate']:.1f}%
• Call→Client: {funnel['conversion']['call_to_client_rate']:.1f}%

---
_Auto-generated 🤖_
"""
    return message

def format_report_legacy(client_name, beehiiv, instagram, web, last_week=None):
    """Legacy format for backward compatibility"""
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
    manual_metrics = get_manual_metrics()
    return format_report(client_name, beehiiv, instagram, web, last_week, manual_metrics)

def get_channel_emoji(channel_type):
    """Get emoji for channel type"""
    emoji_map = {
        'social': '📱',
        'content': '📝',
        'owned': '🌐',
        'paid': '💰',
        'referral': '👥',
        'event': '🎤'
    }
    return emoji_map.get(channel_type, '📊')

def collect_awareness_metrics(client_data, manual_metrics):
    """Dynamically collect awareness metrics based on client's funnel structure"""
    metrics = {}
    errors = []
    
    funnel_structure = client_data.get('funnel_structure', {})
    awareness_channels = funnel_structure.get('awareness', {}).get('channels', [])
    connected_accounts = client_data.get('connected_accounts', {})
    
    for channel in awareness_channels:
        metric_name = channel.get('metric_name', '')
        tracking = channel.get('tracking', 'manual')
        source = channel.get('source', '')
        
        if tracking == 'auto':
            # Fetch from API
            if source == 'vercel':
                project_id = connected_accounts.get('website', {}).get('project_id')
                if project_id and project_id != 'your_vercel_project_id':
                    token = os.getenv('VERCEL_TOKEN')
                    if token and token != 'your_vercel_token':
                        try:
                            web_data = get_vercel_metrics(project_id, token)
                            metrics[metric_name] = web_data.get('visitors', 0)
                        except Exception as e:
                            error_msg = f"⚠️ Vercel API error: {str(e)}"
                            errors.append(error_msg)
                            metrics[metric_name] = 0
                    else:
                        metrics[metric_name] = 0
                else:
                    metrics[metric_name] = 0
            
            elif source == 'instagram':
                user_id = connected_accounts.get('instagram', {}).get('user_id')
                if user_id and user_id != 'your_instagram_user_id':
                    token = connected_accounts.get('instagram', {}).get('access_token') or os.getenv('INSTAGRAM_ACCESS_TOKEN')
                    if token and token != 'your_instagram_access_token':
                        try:
                            ig_data = get_instagram_metrics(user_id, token)
                            metrics[metric_name] = ig_data.get('impressions', 0)
                        except Exception as e:
                            error_msg = f"⚠️ Instagram API error: {str(e)}"
                            errors.append(error_msg)
                            metrics[metric_name] = 0
                    else:
                        metrics[metric_name] = 0
                else:
                    metrics[metric_name] = 0
        else:
            # Manual tracking
            metrics[metric_name] = manual_metrics.get(metric_name, 0)
    
    return metrics, errors

def collect_capture_metrics(client_data):
    """Collect email capture metrics"""
    metrics = {'subscribers': 0, 'open_rate': 0, 'click_rate': 0}
    errors = []
    
    funnel_structure = client_data.get('funnel_structure', {})
    capture_config = funnel_structure.get('capture', {})
    platform = capture_config.get('platform', 'Beehiiv')
    
    # Support legacy structure
    if client_data.get('beehiiv_pub_id'):
        pub_id = client_data['beehiiv_pub_id']
    elif client_data.get('_legacy', {}).get('beehiiv_pub_id'):
        pub_id = client_data['_legacy']['beehiiv_pub_id']
    else:
        connected_accounts = client_data.get('connected_accounts', {})
        email_platform = connected_accounts.get('email_platform', {})
        if email_platform.get('type') == 'beehiiv':
            # Would need pub_id from config, but for now use legacy
            pub_id = None
        else:
            pub_id = None
    
    if pub_id and pub_id != 'your_beehiiv_pub_id':
        api_key = os.getenv('BEEHIIV_API_KEY')
        if api_key and api_key != 'your_beehiiv_api_key':
            try:
                metrics = get_beehiiv_metrics(pub_id, api_key)
            except Exception as e:
                error_msg = f"⚠️ {platform} API error: {str(e)}"
                errors.append(error_msg)
                print(error_msg)
    
    return metrics, errors

def get_client_metrics(client):
    """Get metrics for a single client (supports both old and new structure)"""
    # Initialize defaults
    beehiiv = {'subscribers': 0, 'open_rate': 0, 'click_rate': 0}
    instagram = {'impressions': 0, 'reach': 0}
    web = {'pageviews': 0, 'visitors': 0}
    all_errors = []
    
    # Check if new structure exists
    if client.get('funnel_structure'):
        # New modular structure
        manual_metrics = get_manual_metrics()
        
        # Collect awareness metrics dynamically
        awareness_metrics, awareness_errors = collect_awareness_metrics(client, manual_metrics)
        all_errors.extend(awareness_errors)
        
        # Collect capture metrics
        capture_metrics, capture_errors = collect_capture_metrics(client)
        all_errors.extend(capture_errors)
        beehiiv = capture_metrics
        
        # Map awareness metrics to legacy format for compatibility
        web['visitors'] = awareness_metrics.get('blog_visitors', 0)
        instagram['impressions'] = awareness_metrics.get('ig_impressions', 0)
        
    else:
        # Legacy structure - backward compatibility
        # Beehiiv
        if client.get('beehiiv_pub_id') and client['beehiiv_pub_id'] != 'your_beehiiv_pub_id':
            api_key = os.getenv('BEEHIIV_API_KEY')
            if api_key and api_key != 'your_beehiiv_api_key':
                try:
                    beehiiv = get_beehiiv_metrics(client['beehiiv_pub_id'], api_key)
                except Exception as e:
                    error_msg = f"⚠️ Beehiiv API error: {str(e)}"
                    all_errors.append(error_msg)
                    print(error_msg)
        
        # Instagram
        if client.get('instagram_id') and client['instagram_id'] != 'your_instagram_user_id':
            token = client.get('instagram_token') or os.getenv('INSTAGRAM_ACCESS_TOKEN')
            if token and token != 'your_instagram_access_token':
                try:
                    instagram = get_instagram_metrics(client['instagram_id'], token)
                except Exception as e:
                    error_msg = f"⚠️ Instagram API error: {str(e)}"
                    all_errors.append(error_msg)
                    print(error_msg)
        
        # Vercel
        if client.get('vercel_project_id') and client['vercel_project_id'] != 'your_vercel_project_id':
            token = os.getenv('VERCEL_TOKEN')
            if token and token != 'your_vercel_token':
                try:
                    web = get_vercel_metrics(client['vercel_project_id'], token)
                except Exception as e:
                    error_msg = f"⚠️ Vercel API error: {str(e)}"
                    all_errors.append(error_msg)
                    print(error_msg)
    
    return beehiiv, instagram, web, all_errors


def get_week_key(date=None):
    """Get week key in format week_YYYY-MM-DD for Monday of that week"""
    if date is None:
        date = datetime.now()
    # Get Monday of the week
    days_since_monday = date.weekday()
    monday = date - timedelta(days=days_since_monday)
    return f"week_{monday.strftime('%Y-%m-%d')}"

def get_manual_metrics(week_key=None):
    """Load manual tracking metrics from JSON file"""
    if week_key is None:
        week_key = get_week_key()
    
    try:
        if os.path.exists('manual_metrics.json'):
            with open('manual_metrics.json', 'r') as f:
                data = json.load(f)
                return data.get(week_key, {})
    except Exception as e:
        print(f"⚠️  Error loading manual metrics: {e}")
    return {}

def save_manual_metric(metric_name, value, week_key=None):
    """Save a manual metric to the JSON file"""
    if week_key is None:
        week_key = get_week_key()
    
    try:
        data = {}
        if os.path.exists('manual_metrics.json'):
            with open('manual_metrics.json', 'r') as f:
                data = json.load(f)
        
        if week_key not in data:
            data[week_key] = {}
        
        data[week_key][metric_name] = value
        data[week_key]['last_updated'] = datetime.now().isoformat()
        
        with open('manual_metrics.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
    except Exception as e:
        print(f"⚠️  Error saving manual metric: {e}")
        return False

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

def prepare_detailed_metrics(beehiiv, instagram, web, manual_metrics, last_week=None, client_data=None):
    """Prepare metrics dict for detailed report formatter - supports dynamic channels"""
    if client_data is None:
        client_data = {}
    
    # Collect all awareness metrics dynamically
    awareness_metrics = {}
    funnel_structure = client_data.get('funnel_structure', {})
    awareness_channels = funnel_structure.get('awareness', {}).get('channels', [])
    
    # If no new structure, use legacy defaults
    if not awareness_channels:
        awareness_metrics = {
            'blog_visitors': web.get('visitors', 0),
            'ig_impressions': instagram.get('impressions', 0),
            'linkedin_impressions': manual_metrics.get('linkedin_impressions', 0)
        }
    else:
        # Collect from manual metrics and API results
        for channel in awareness_channels:
            metric_name = channel.get('metric_name', '')
            source = channel.get('source', '')
            
            if source == 'vercel':
                awareness_metrics[metric_name] = web.get('visitors', 0)
            elif source == 'instagram':
                awareness_metrics[metric_name] = instagram.get('impressions', 0)
            else:
                # Manual tracking
                awareness_metrics[metric_name] = manual_metrics.get(metric_name, 0)
    
    # Calculate total reach
    total_reach = sum(awareness_metrics.values())
    
    # Calculate capture rate (new subscribers / total awareness)
    new_subscribers = manual_metrics.get('new_subscribers', 0)
    capture_rate = (new_subscribers / total_reach * 100) if total_reach > 0 else 0
    
    # Calculate inquiry and close rates
    inquiry_rate = (manual_metrics.get('inquiries', 0) / beehiiv.get('subscribers', 1)) * 100 if beehiiv.get('subscribers', 0) > 0 else 0
    close_rate = (manual_metrics.get('retainer_signups', 0) / manual_metrics.get('calls_booked', 1)) * 100 if manual_metrics.get('calls_booked', 0) > 0 else 0
    
    # Calculate opens and clicks
    opens = int(beehiiv.get('subscribers', 0) * beehiiv.get('open_rate', 0) / 100)
    clicks = int(beehiiv.get('subscribers', 0) * beehiiv.get('click_rate', 0) / 100)
    
    # Build metrics dict with all awareness channels
    metrics = {
        **awareness_metrics,  # Include all dynamic awareness metrics
        'total_reach': total_reach,
        'new_subscribers': new_subscribers,
        'total_subscribers': beehiiv.get('subscribers', 0),
        'capture_rate': capture_rate,
        'open_rate': beehiiv.get('open_rate', 0),
        'click_rate': beehiiv.get('click_rate', 0),
        'opens': opens,
        'clicks': clicks,
        'inquiries': manual_metrics.get('inquiries', 0),
        'calls_booked': manual_metrics.get('calls_booked', 0),
        'new_clients': manual_metrics.get('retainer_signups', 0),
        'inquiry_rate': inquiry_rate,
        'close_rate': close_rate,
    }
    
    # Add last week data if available
    if last_week:
        metrics['blog_visitors_last_week'] = last_week.get('web', {}).get('visitors', metrics.get('blog_visitors', 0))
        metrics['ig_impressions_last_week'] = last_week.get('instagram', {}).get('impressions', metrics.get('ig_impressions', 0))
        metrics['new_subscribers_last_week'] = last_week.get('beehiiv', {}).get('subscribers', 0)
    
    return metrics

def format_detailed_report(client_name, beehiiv, instagram, web, last_week=None, manual_metrics=None, client_data=None):
    """Generate detailed report with interpretations - supports dynamic funnels"""
    from report_formatter import format_detailed_report as format_detailed
    
    if manual_metrics is None:
        manual_metrics = get_manual_metrics()
    
    if client_data is None:
        client_data = {}
    
    # Prepare metrics for detailed formatter (includes dynamic awareness channels)
    metrics = prepare_detailed_metrics(beehiiv, instagram, web, manual_metrics, last_week, client_data)
    
    # Prepare last week dict for formatter
    last_week_dict = {}
    if last_week:
        last_week_dict = {
            'blog_visitors': last_week.get('web', {}).get('visitors', 0),
            'ig_impressions': last_week.get('instagram', {}).get('impressions', 0),
            'new_subscribers': last_week.get('beehiiv', {}).get('subscribers', 0),
            'total_subscribers': last_week.get('beehiiv', {}).get('subscribers', 0),
        }
    
    return format_detailed(metrics, last_week_dict, client_data)

def send_all_reports(use_detailed=True):
    """Send reports to all clients"""
    with open('clients.json', 'r') as f:
        data = json.load(f)
    
    # Get manual metrics for current week
    manual_metrics = get_manual_metrics()
    
    for client in data['clients']:
        try:
            # Get current metrics
            beehiiv, instagram, web, errors = get_client_metrics(client)
            
            # Get last week's metrics for comparison
            last_week = load_last_week_metrics(client['name'])
            
            # Format report (detailed for weekly, simple for on-demand)
            if use_detailed:
                report = format_detailed_report(client['name'], beehiiv, instagram, web, last_week, manual_metrics, client)
            else:
                report = format_report(client['name'], beehiiv, instagram, web, last_week, manual_metrics)
            
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


