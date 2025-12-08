"""
Content pillar performance tracking
"""
import json
import os
from datetime import datetime, timedelta
from .center_post import get_post, list_posts

CONTENT_METRICS_FILE = 'content_metrics.json'
CONTENT_PILLARS_FILE = 'content_pillars.json'

def load_pillars():
    """Load pillar definitions"""
    if os.path.exists(CONTENT_PILLARS_FILE):
        with open(CONTENT_PILLARS_FILE, 'r') as f:
            return json.load(f)
    return {"pillars": []}

def save_pillars(data):
    """Save pillar definitions"""
    with open(CONTENT_PILLARS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_metrics():
    """Load content metrics"""
    if os.path.exists(CONTENT_METRICS_FILE):
        with open(CONTENT_METRICS_FILE, 'r') as f:
            return json.load(f)
    return {"metrics": {}}

def save_metrics(data):
    """Save content metrics"""
    with open(CONTENT_METRICS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def create_pillar(client_id, name, color, channels=None, target_audience=None):
    """
    Create a new content pillar
    
    Args:
        client_id: Client identifier
        name: Pillar name (e.g., "Education")
        color: Hex color code
        channels: List of channels this pillar uses
        target_audience: Target audience description
    """
    import uuid
    pillar_id = f"pillar_{uuid.uuid4().hex[:12]}"
    
    data = load_pillars()
    pillar = {
        "id": pillar_id,
        "name": name,
        "color": color,
        "client_id": client_id,
        "channels": channels or [],
        "target_audience": target_audience,
        "created_at": datetime.now().isoformat()
    }
    
    data['pillars'].append(pillar)
    save_pillars(data)
    return pillar

def get_pillars(client_id=None):
    """Get pillars, optionally filtered by client"""
    data = load_pillars()
    pillars = data.get('pillars', [])
    
    if client_id:
        pillars = [p for p in pillars if p.get('client_id') == client_id]
    
    return pillars

def track_content_performance(post_id, metrics):
    """
    Track how content performs in funnel
    
    Args:
        post_id: Content post ID
        metrics: Dict with funnel metrics
            {
                "funnel_impact": {
                    "awareness": {"blog_visitors": 150, ...},
                    "capture": {"new_subscribers": 5},
                    "conversion": {"inquiries": 1}
                },
                "derivatives_performance": {
                    "newsletter": {"opens": 120, "clicks": 15}
                }
            }
    """
    post = get_post(post_id)
    if not post:
        raise ValueError(f"Post {post_id} not found")
    
    data = load_metrics()
    if 'metrics' not in data:
        data['metrics'] = {}
    
    data['metrics'][post_id] = {
        "pillar_id": post.get('pillar_id'),
        "funnel_impact": metrics.get('funnel_impact', {}),
        "derivatives_performance": metrics.get('derivatives_performance', {}),
        "updated_at": datetime.now().isoformat()
    }
    
    save_metrics(data)
    return data['metrics'][post_id]

def get_pillar_performance(pillar_id, date_range_days=30):
    """
    Aggregate performance by pillar
    
    Args:
        pillar_id: Pillar ID
        date_range_days: Number of days to look back
    
    Returns:
        dict: Aggregated metrics for the pillar
    """
    cutoff_date = datetime.now() - timedelta(days=date_range_days)
    
    # Get all posts for this pillar
    all_posts = list_posts()
    pillar_posts = [p for p in all_posts if p.get('pillar_id') == pillar_id]
    
    # Get metrics for these posts
    metrics_data = load_metrics()
    all_metrics = metrics_data.get('metrics', {})
    
    # Aggregate
    total_awareness = {}
    total_capture = {}
    total_conversion = {}
    total_derivatives = {}
    
    for post in pillar_posts:
        post_id = post['id']
        post_metrics = all_metrics.get(post_id, {})
        
        funnel_impact = post_metrics.get('funnel_impact', {})
        
        # Aggregate awareness
        awareness = funnel_impact.get('awareness', {})
        for key, value in awareness.items():
            total_awareness[key] = total_awareness.get(key, 0) + value
        
        # Aggregate capture
        capture = funnel_impact.get('capture', {})
        for key, value in capture.items():
            total_capture[key] = total_capture.get(key, 0) + value
        
        # Aggregate conversion
        conversion = funnel_impact.get('conversion', {})
        for key, value in conversion.items():
            total_conversion[key] = total_conversion.get(key, 0) + value
        
        # Aggregate derivatives
        derivatives = post_metrics.get('derivatives_performance', {})
        for platform, perf in derivatives.items():
            if platform not in total_derivatives:
                total_derivatives[platform] = {}
            for metric, value in perf.items():
                total_derivatives[platform][metric] = total_derivatives[platform].get(metric, 0) + value
    
    return {
        "pillar_id": pillar_id,
        "post_count": len(pillar_posts),
        "funnel_impact": {
            "awareness": total_awareness,
            "capture": total_capture,
            "conversion": total_conversion
        },
        "derivatives_performance": total_derivatives,
        "date_range_days": date_range_days
    }

def get_content_performance(post_id):
    """Get performance metrics for a specific post"""
    data = load_metrics()
    return data.get('metrics', {}).get(post_id, {})

