"""
Content pillar performance tracking
"""
import json
import os
from datetime import datetime, timedelta
from .center_post import get_post, list_posts

CONTENT_METRICS_FILE = 'content_metrics.json'
CONTENT_PILLARS_FILE = 'content_pillars.json'

def load_pillars(client_id=None):
    """Load pillar definitions from Supabase, file, or memory cache"""
    # Try Supabase first (recommended)
    try:
        from .supabase_storage import load_pillars_from_supabase
        pillars = load_pillars_from_supabase(client_id=client_id)
        if pillars:
            return {"pillars": pillars}
    except Exception as e:
        print(f"⚠️ Supabase not available: {e}")
    
    # Fallback to file (for local development)
    if os.path.exists(CONTENT_PILLARS_FILE):
        try:
            with open(CONTENT_PILLARS_FILE, 'r') as f:
                file_data = json.load(f)
                pillars = file_data.get('pillars', [])
                if client_id:
                    pillars = [p for p in pillars if p.get('client_id') == client_id]
                return {"pillars": pillars}
        except Exception as e:
            print(f"⚠️ Warning: Could not load {CONTENT_PILLARS_FILE}: {e}")
    return {"pillars": []}

def save_pillars(data):
    """Save pillar definitions to Supabase, file, or memory cache"""
    pillars = data.get('pillars', [])
    
    # Try Supabase first (recommended)
    supabase_saved = False
    try:
        from .supabase_storage import save_pillars_to_supabase
        if save_pillars_to_supabase(pillars):
            print("✅ Saved pillars to Supabase")
            supabase_saved = True
    except Exception as e:
        print(f"⚠️ Supabase save failed: {e}")
    
    # Fallback to file (for local development)
    if not supabase_saved:
        try:
            with open(CONTENT_PILLARS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            print("✅ Saved pillars to file")
        except (OSError, PermissionError) as e:
            # Handle read-only filesystem (e.g., on Vercel)
            print(f"⚠️ Warning: Could not save to {CONTENT_PILLARS_FILE}: {e}")
            print("   This is expected on read-only filesystems (e.g., Vercel).")
            print("   Pillar data is returned but not persisted to disk.")
            print("   To persist data, set up Supabase or Vercel KV.")
            # Don't raise - allow the function to continue

def load_metrics(post_id=None, pillar_id=None):
    """Load content metrics from Supabase, file, or memory cache"""
    # Try Supabase first (recommended)
    try:
        from .supabase_storage import load_metrics_from_supabase
        supabase_data = load_metrics_from_supabase(post_id=post_id, pillar_id=pillar_id)
        if supabase_data:
            return supabase_data
    except Exception as e:
        print(f"⚠️ Supabase not available: {e}")
    
    # Fallback to file (for local development)
    if os.path.exists(CONTENT_METRICS_FILE):
        try:
            with open(CONTENT_METRICS_FILE, 'r') as f:
                file_data = json.load(f)
                metrics = file_data.get('metrics', {})
                # Filter by post_id or pillar_id if needed
                if post_id or pillar_id:
                    # This is a simplified filter - adjust based on your metrics structure
                    filtered_metrics = {}
                    for key, value in metrics.items():
                        if post_id and value.get('post_id') != post_id:
                            continue
                        if pillar_id and value.get('pillar_id') != pillar_id:
                            continue
                        filtered_metrics[key] = value
                    return {"metrics": filtered_metrics}
                return file_data
        except Exception as e:
            print(f"⚠️ Warning: Could not load {CONTENT_METRICS_FILE}: {e}")
    return {"metrics": {}}

def save_metrics(data):
    """Save content metrics"""
    try:
        with open(CONTENT_METRICS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except (OSError, PermissionError) as e:
        # Handle read-only filesystem (e.g., on Vercel)
        print(f"⚠️ Warning: Could not save to {CONTENT_METRICS_FILE}: {e}")
        print("   This is expected on read-only filesystems (e.g., Vercel).")
        print("   Metrics data is returned but not persisted to disk.")
        # Don't raise - allow the function to continue

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

