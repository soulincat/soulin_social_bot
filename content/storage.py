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
    # Try REST API first (Vercel KV uses REST, not direct Redis connection)
    try:
        import requests
        kv_url = os.getenv('KV_REST_API_URL')
        kv_token = os.getenv('KV_REST_API_TOKEN')
        
        if kv_url and kv_token:
            # Vercel KV REST API format: POST to /get with JSON body
            response = requests.post(
                f"{kv_url}/get",
                headers={
                    "Authorization": f"Bearer {kv_token}",
                    "Content-Type": "application/json"
                },
                json={"key": key}
            )
            if response.status_code == 200:
                result = response.json()
                # Vercel KV returns {"result": "value"} or {"result": null}
                if result.get('result'):
                    value = result['result']
                    return json.loads(value) if isinstance(value, str) else value
            else:
                print(f"⚠️ KV GET failed: {response.status_code} - {response.text}")
    except ImportError:
        pass
    except Exception as e:
        print(f"⚠️ Error loading from KV (REST): {e}")
    
    # Fallback to direct Redis connection if available
    if KV_AVAILABLE and redis_client:
        try:
            data = redis_client.get(key)
            if data:
                return json.loads(data) if isinstance(data, str) else data
        except Exception as e:
            print(f"⚠️ Error loading from KV (direct): {e}")
    
    return None

def save_to_kv(key, data):
    """Save data to Vercel KV using REST API"""
    # Try REST API first (Vercel KV uses REST, not direct Redis connection)
    try:
        import requests
        kv_url = os.getenv('KV_REST_API_URL')
        kv_token = os.getenv('KV_REST_API_TOKEN')
        
        if kv_url and kv_token:
            # Vercel KV REST API format: POST to /set with JSON body
            response = requests.post(
                f"{kv_url}/set",
                headers={
                    "Authorization": f"Bearer {kv_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "key": key,
                    "value": json.dumps(data)
                }
            )
            if response.status_code == 200:
                print(f"✅ Successfully saved to KV: {key}")
                return True
            else:
                print(f"⚠️ KV SET failed: {response.status_code} - {response.text}")
    except ImportError:
        print("⚠️ requests library not available for KV REST API")
    except Exception as e:
        print(f"⚠️ Error saving to KV (REST): {e}")
    
    # Fallback to direct Redis connection if available
    if KV_AVAILABLE and redis_client:
        try:
            redis_client.set(key, json.dumps(data))
            print(f"✅ Successfully saved to KV (direct): {key}")
            return True
        except Exception as e:
            print(f"⚠️ Error saving to KV (direct): {e}")
    
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

