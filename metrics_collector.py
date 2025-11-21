"""
Dynamic metric collection system - fetches metrics based on client's funnel structure
"""
import os
import json
import requests
from datetime import datetime, timedelta
from bot import get_beehiiv_metrics, get_instagram_metrics, get_vercel_metrics

def fetch_from_api(source, connection, metric_name=None):
    """
    Router function that calls the right API based on source.
    Returns the metric value for the specified metric_name.
    """
    try:
        if source == 'instagram':
            user_id = connection.get('user_id')
            access_token = connection.get('access_token') or os.getenv('INSTAGRAM_ACCESS_TOKEN')
            if not user_id or not access_token:
                return 0
            data = get_instagram_metrics(user_id, access_token)
            # Return impressions for ig_impressions, reach for ig_reach, etc.
            if 'impressions' in metric_name.lower():
                return data.get('impressions', 0)
            elif 'reach' in metric_name.lower():
                return data.get('reach', 0)
            return data.get('impressions', 0)
        
        elif source == 'vercel':
            project_id = connection.get('project_id')
            token = connection.get('token') or os.getenv('VERCEL_TOKEN')
            if not project_id or not token:
                return 0
            data = get_vercel_metrics(project_id, token)
            if 'visitors' in metric_name.lower():
                return data.get('visitors', 0)
            elif 'pageviews' in metric_name.lower():
                return data.get('pageviews', 0)
            return data.get('visitors', 0)
        
        elif source == 'beehiiv':
            pub_id = connection.get('pub_id')
            api_key = connection.get('api_key') or os.getenv('BEEHIIV_API_KEY')
            if not pub_id or not api_key:
                return 0
            data = get_beehiiv_metrics(pub_id, api_key)
            return data  # Returns dict with subscribers, open_rate, click_rate
        
        else:
            raise ValueError(f"Unknown source: {source}")
    
    except Exception as e:
        print(f"❌ Error fetching from {source}: {e}")
        raise

def get_manual_metric(scope_id, metric_name, week_key=None):
    """
    Get manually entered metric from manual_metrics.json
    Structure: {client_id: {week_key: {metric_name: value}}}
    Falls back to old structure: {week_key: {metric_name: value}} for backward compatibility
    """
    if week_key is None:
        week_key = datetime.now().strftime('%Y-%m-%d')
    
    try:
        if os.path.exists('manual_metrics.json'):
            with open('manual_metrics.json', 'r') as f:
                data = json.load(f)
                if scope_id in data:
                    return data.get(scope_id, {}).get(week_key, {}).get(metric_name, 0)
                # Fall back to old structure (legacy)
                return data.get(week_key, {}).get(metric_name, 0)
    except Exception as e:
        print(f"⚠️ Error loading manual metric: {e}")
    return 0

def save_manual_metric(scope_id, metric_name, value, week_key=None):
    """
    Save manual metric to JSON file.
    Structure: {client_id: {week_key: {metric_name: value}}}
    """
    if week_key is None:
        week_key = datetime.now().strftime('%Y-%m-%d')
    
    try:
        data = {}
        if os.path.exists('manual_metrics.json'):
            with open('manual_metrics.json', 'r') as f:
                data = json.load(f)
        
        if scope_id not in data:
            data[scope_id] = {}
        
        if week_key not in data[scope_id]:
            data[scope_id][week_key] = {}
        
        data[scope_id][week_key][metric_name] = value
        data[scope_id][week_key]['last_updated'] = datetime.now().isoformat()
        
        with open('manual_metrics.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
    except Exception as e:
        print(f"⚠️ Error saving manual metric: {e}")
        return False

def get_manual_metrics_list(client_data, project_data=None):
    """
    Generate list of metrics this client needs to track manually.
    """
    metrics = []
    source = project_data or client_data
    funnel_structure = source.get('funnel_structure', {})
    
    # Check awareness channels
    for channel in funnel_structure.get('awareness', {}).get('channels', []):
        if channel.get('tracking') == 'manual':
            metric_name = channel.get('metric_name', '')
            channel_name = channel.get('name', 'Unknown')
            metrics.append(f"• {metric_name} (for {channel_name})")
    
    # Check conversion touchpoints
    for tp in funnel_structure.get('conversion', {}).get('touchpoints', []):
        if tp.get('tracking') == 'manual':
            metric_name = tp.get('metric_name', '')
            tp_name = tp.get('name', 'Unknown')
            metrics.append(f"• {metric_name} ({tp_name})")
    
    return metrics

def is_valid_metric(client_data, metric_name, project_data=None):
    """
    Check if metric_name exists in client's funnel structure.
    """
    source = project_data or client_data
    funnel_structure = source.get('funnel_structure', {})
    
    # Check awareness
    for channel in funnel_structure.get('awareness', {}).get('channels', []):
        if channel.get('metric_name') == metric_name:
            return True
    
    # Check conversion
    for tp in funnel_structure.get('conversion', {}).get('touchpoints', []):
        if tp.get('metric_name') == metric_name:
            return True
    
    return False

def collect_all_metrics(client_data, project_data=None):
    """
    Dynamically collect metrics based on client's funnel structure.
    Handles any combination of channels, platforms, tracking methods.
    Returns metrics dict with graceful error handling.
    """
    client_id = client_data.get('client_id', 'unknown')
    project = project_data or {}
    scope_id = project.get('scope_id') or client_id
    metrics = {
        'awareness': {},
        'capture': {},
        'nurture': {},
        'conversion': {},
        'errors': []
    }
    
    funnel_structure = project.get('funnel_structure', {}) or client_data.get('funnel_structure', {})
    
    # AWARENESS - loop through all channels
    total_reach = 0
    for channel in funnel_structure.get('awareness', {}).get('channels', []):
        try:
            channel_name = channel.get('name', 'Unknown')
            tracking = channel.get('tracking', 'manual')
            metric_name = channel.get('metric_name', '')
            
            if tracking == 'auto':
                # Fetch from API based on source
                source = channel.get('source')
                api_connection = channel.get('api_connection', {})
                
                if not source or not api_connection:
                    metrics['errors'].append(f"{channel_name}: Missing API connection config")
                    metrics['awareness'][channel_name] = 0
                    continue
                
                value = fetch_from_api(source, api_connection, metric_name)
                metrics['awareness'][channel_name] = value
                total_reach += value
                
            else:
                # Get from manual_metrics.json
                value = get_manual_metric(scope_id, metric_name)
                metrics['awareness'][channel_name] = value
                total_reach += value
                
        except Exception as e:
            error_msg = f"{channel.get('name', 'Unknown')}: {str(e)}"
            metrics['errors'].append(error_msg)
            metrics['awareness'][channel.get('name', 'Unknown')] = 0
            print(f"❌ Error fetching {channel.get('name')}: {e}")
    
    metrics['total_reach'] = total_reach
    
    # CAPTURE
    try:
        capture_config = funnel_structure.get('capture', {})
        if capture_config.get('tracking') == 'auto':
            platform_id = capture_config.get('platform_id', 'beehiiv')
            api_connection = capture_config.get('api_connection', {})
            
            if platform_id == 'beehiiv':
                pub_id = api_connection.get('pub_id')
                api_key = api_connection.get('api_key') or os.getenv('BEEHIIV_API_KEY')
                
                if pub_id and api_key:
                    capture_data = get_beehiiv_metrics(pub_id, api_key)
                    # Calculate new subscribers (would need last week's data)
                    metrics['capture'] = {
                        'total_subscribers': capture_data.get('subscribers', 0),
                        'new_subscribers': 0,  # Will be calculated from history
                        'open_rate': capture_data.get('open_rate', 0),
                        'click_rate': capture_data.get('click_rate', 0),
                        'opens': int(capture_data.get('subscribers', 0) * capture_data.get('open_rate', 0) / 100),
                        'clicks': int(capture_data.get('subscribers', 0) * capture_data.get('click_rate', 0) / 100)
                    }
                else:
                    metrics['capture'] = {'total_subscribers': 0, 'new_subscribers': 0, 'open_rate': 0, 'click_rate': 0, 'opens': 0, 'clicks': 0}
            else:
                metrics['capture'] = {'total_subscribers': 0, 'new_subscribers': 0, 'open_rate': 0, 'click_rate': 0, 'opens': 0, 'clicks': 0}
        else:
            # Manual capture tracking
            metrics['capture'] = {
                'total_subscribers': get_manual_metric(scope_id, 'total_subscribers'),
                'new_subscribers': get_manual_metric(scope_id, 'new_subscribers'),
                'open_rate': 0,
                'click_rate': 0,
                'opens': 0,
                'clicks': 0
            }
    except Exception as e:
        metrics['errors'].append(f"Email capture: {str(e)}")
        metrics['capture'] = {
            'total_subscribers': 0,
            'new_subscribers': 0,
            'open_rate': 0,
            'click_rate': 0,
            'opens': 0,
            'clicks': 0
        }
    
    # NURTURE (usually same as capture platform)
    metrics['nurture'] = {
        'open_rate': metrics['capture'].get('open_rate', 0),
        'click_rate': metrics['capture'].get('click_rate', 0),
        'opens': metrics['capture'].get('opens', 0),
        'clicks': metrics['capture'].get('clicks', 0)
    }
    
    # CONVERSION - loop through touchpoints
    for touchpoint in funnel_structure.get('conversion', {}).get('touchpoints', []):
        try:
            tp_name = touchpoint.get('name', 'Unknown')
            metric_name = touchpoint.get('metric_name', '')
            value = get_manual_metric(scope_id, metric_name)
            metrics['conversion'][tp_name] = value
        except Exception as e:
            metrics['errors'].append(f"{touchpoint.get('name')}: {str(e)}")
            metrics['conversion'][touchpoint.get('name', 'Unknown')] = 0
    
    # Calculate conversion rates
    capture_rate = 0
    if metrics['total_reach'] > 0:
        capture_rate = (metrics['capture'].get('new_subscribers', 0) / metrics['total_reach']) * 100
    
    inquiry_rate = 0
    if metrics['capture'].get('total_subscribers', 0) > 0:
        total_inquiries = sum([v for k, v in metrics['conversion'].items() if 'inquiry' in k.lower() or 'call' in k.lower()])
        inquiry_rate = (total_inquiries / metrics['capture'].get('total_subscribers', 1)) * 100
    
    close_rate = 0
    calls = metrics['conversion'].get('calls_booked', 0) or metrics['conversion'].get('Discovery call', 0)
    clients = metrics['conversion'].get('new_clients', 0) or metrics['conversion'].get('Retainer', 0)
    if calls > 0:
        close_rate = (clients / calls) * 100
    
    metrics['rates'] = {
        'capture_rate': capture_rate,
        'inquiry_rate': inquiry_rate,
        'close_rate': close_rate
    }
    
    metrics['fans_total'] = metrics['capture'].get('total_subscribers', 0)
    revenue_manual = get_manual_metric(scope_id, 'monthly_revenue')
    metrics['monthly_revenue'] = revenue_manual or 0
    metrics['scope_id'] = scope_id
    metrics['project_name'] = project.get('project_name', client_data.get('name'))
    metrics['project_id'] = project.get('project_id')
    
    return metrics

