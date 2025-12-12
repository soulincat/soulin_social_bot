"""
Storage abstraction layer for content data
Supports both file-based storage (local) and Vercel KV/Redis (production)
"""
import json
import os

# Try to import Redis for Vercel KV
KV_AVAILABLE = False
redis_client = None

try:
    import redis
    # Vercel KV uses Redis - get connection from environment
    kv_url = os.getenv('KV_REST_API_URL')
    kv_token = os.getenv('KV_REST_API_TOKEN')
    
    if kv_url and kv_token:
        # Parse URL (format: https://xxx.upstash.io)
        # Vercel KV uses REST API, so we need to use requests or redis with REST
        # For simplicity, we'll use redis-py with REST API
        redis_client = redis.from_url(
            kv_url.replace('https://', 'rediss://'),
            password=kv_token,
            decode_responses=True
        )
        # Test connection
        try:
            redis_client.ping()
            KV_AVAILABLE = True
            print("✅ Connected to Vercel KV")
        except:
            # If direct connection fails, try REST API approach
            redis_client = None
except ImportError:
    pass
except Exception as e:
    print(f"⚠️ Could not connect to KV: {e}")

def get_storage_key(key_type, key_id=None):
    """Generate storage key for KV"""
    if key_id:
        return f"content:{key_type}:{key_id}"
    return f"content:{key_type}"

def load_from_kv(key):
    """Load data from Vercel KV using REST API"""
    if not KV_AVAILABLE or not redis_client:
        return None
    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data) if isinstance(data, str) else data
    except Exception as e:
        # Try REST API approach if direct connection fails
        try:
            import requests
            kv_url = os.getenv('KV_REST_API_URL')
            kv_token = os.getenv('KV_REST_API_TOKEN')
            if kv_url and kv_token:
                response = requests.get(
                    f"{kv_url}/get/{key}",
                    headers={"Authorization": f"Bearer {kv_token}"}
                )
                if response.status_code == 200:
                    result = response.json()
                    if result.get('result'):
                        return json.loads(result['result']) if isinstance(result['result'], str) else result['result']
        except Exception as e2:
            print(f"⚠️ Error loading from KV (REST): {e2}")
    return None

def save_to_kv(key, data):
    """Save data to Vercel KV using REST API"""
    if not KV_AVAILABLE or not redis_client:
        # Try REST API directly
        try:
            import requests
            kv_url = os.getenv('KV_REST_API_URL')
            kv_token = os.getenv('KV_REST_API_TOKEN')
            if kv_url and kv_token:
                response = requests.post(
                    f"{kv_url}/set/{key}",
                    headers={"Authorization": f"Bearer {kv_token}"},
                    json={"value": json.dumps(data)}
                )
                if response.status_code == 200:
                    return True
        except Exception as e:
            print(f"⚠️ Error saving to KV (REST): {e}")
        return False
    
    try:
        redis_client.set(key, json.dumps(data))
        return True
    except Exception as e:
        # Fallback to REST API
        try:
            import requests
            kv_url = os.getenv('KV_REST_API_URL')
            kv_token = os.getenv('KV_REST_API_TOKEN')
            if kv_url and kv_token:
                response = requests.post(
                    f"{kv_url}/set/{key}",
                    headers={"Authorization": f"Bearer {kv_token}"},
                    json={"value": json.dumps(data)}
                )
                return response.status_code == 200
        except Exception as e2:
            print(f"⚠️ Error saving to KV: {e2}")
        return False

def load_posts():
    """Load posts from KV or return None if not available"""
    key = get_storage_key("posts")
    return load_from_kv(key)

def save_posts(data):
    """Save posts to KV"""
    key = get_storage_key("posts")
    return save_to_kv(key, data)

def load_derivatives():
    """Load derivatives from KV or return None if not available"""
    key = get_storage_key("derivatives")
    return load_from_kv(key)

def save_derivatives(data):
    """Save derivatives to KV"""
    key = get_storage_key("derivatives")
    return save_to_kv(key, data)

def load_pillars():
    """Load pillars from KV or return None if not available"""
    key = get_storage_key("pillars")
    return load_from_kv(key)

def save_pillars(data):
    """Save pillars to KV"""
    key = get_storage_key("pillars")
    return save_to_kv(key, data)

def load_metrics():
    """Load metrics from KV or return None if not available"""
    key = get_storage_key("metrics")
    return load_from_kv(key)

def save_metrics(data):
    """Save metrics to KV"""
    key = get_storage_key("metrics")
    return save_to_kv(key, data)

