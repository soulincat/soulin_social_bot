"""
Supabase storage layer for content system
Replaces JSON file and KV storage with PostgreSQL via Supabase
"""
import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

# Try to import Supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

_supabase_client: Optional[Client] = None

def get_supabase_client() -> Optional[Client]:
    """Get or create Supabase client"""
    global _supabase_client
    
    if not SUPABASE_AVAILABLE:
        return None
    
    if _supabase_client is None:
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_ANON_KEY')
        
        if supabase_url and supabase_key:
            try:
                _supabase_client = create_client(supabase_url, supabase_key)
                print("✅ Connected to Supabase")
                return _supabase_client
            except Exception as e:
                print(f"⚠️ Error connecting to Supabase: {e}")
                return None
        else:
            print("⚠️ Supabase credentials not found (SUPABASE_URL and SUPABASE_KEY)")
            return None
    
    return _supabase_client

# ==================== POSTS ====================

def load_posts_from_supabase() -> Dict[str, Any]:
    """Load all posts from Supabase"""
    client = get_supabase_client()
    if not client:
        return {"posts": []}
    
    try:
        response = client.table('posts').select('*').order('created_at', desc=True).execute()
        posts = response.data if response.data else []
        return {"posts": posts}
    except Exception as e:
        print(f"⚠️ Error loading posts from Supabase: {e}")
        return {"posts": []}

def save_posts_to_supabase(posts: List[Dict[str, Any]]) -> bool:
    """Save posts to Supabase (upsert)"""
    client = get_supabase_client()
    if not client:
        return False
    
    try:
        # Upsert all posts
        for post in posts:
            # Convert datetime strings to ISO format if needed
            post_data = post.copy()
            if 'created_at' in post_data and isinstance(post_data['created_at'], str):
                # Already a string, keep it
                pass
            elif 'created_at' in post_data:
                post_data['created_at'] = post_data['created_at'].isoformat() if hasattr(post_data['created_at'], 'isoformat') else str(post_data['created_at'])
            
            if 'updated_at' in post_data and isinstance(post_data['updated_at'], str):
                pass
            elif 'updated_at' in post_data:
                post_data['updated_at'] = post_data['updated_at'].isoformat() if hasattr(post_data['updated_at'], 'isoformat') else str(post_data['updated_at'])
            
            # Ensure JSONB fields are dicts, not strings
            for jsonb_field in ['center_post', 'archive_version', 'blog_version']:
                if jsonb_field in post_data and isinstance(post_data[jsonb_field], str):
                    try:
                        post_data[jsonb_field] = json.loads(post_data[jsonb_field])
                    except:
                        pass
            
            client.table('posts').upsert(post_data, on_conflict='id').execute()
        
        print(f"✅ Saved {len(posts)} posts to Supabase")
        return True
    except Exception as e:
        print(f"⚠️ Error saving posts to Supabase: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_post_from_supabase(post_id: str) -> Optional[Dict[str, Any]]:
    """Get a single post from Supabase"""
    client = get_supabase_client()
    if not client:
        return None
    
    try:
        response = client.table('posts').select('*').eq('id', post_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"⚠️ Error getting post from Supabase: {e}")
        return None

# ==================== DERIVATIVES ====================

def load_derivatives_from_supabase(post_id: Optional[str] = None) -> Dict[str, Any]:
    """Load derivatives from Supabase, optionally filtered by post_id"""
    client = get_supabase_client()
    if not client:
        return {"derivatives": []}
    
    try:
        query = client.table('derivatives').select('*')
        if post_id:
            query = query.eq('post_id', post_id)
        response = query.order('created_at', desc=True).execute()
        derivatives = response.data if response.data else []
        return {"derivatives": derivatives}
    except Exception as e:
        print(f"⚠️ Error loading derivatives from Supabase: {e}")
        return {"derivatives": []}

def save_derivatives_to_supabase(derivatives: List[Dict[str, Any]]) -> bool:
    """Save derivatives to Supabase (upsert)"""
    client = get_supabase_client()
    if not client:
        return False
    
    try:
        for deriv in derivatives:
            deriv_data = deriv.copy()
            
            # Convert datetime strings
            for date_field in ['created_at', 'updated_at', 'scheduled_for', 'published_at']:
                if date_field in deriv_data and not isinstance(deriv_data[date_field], str):
                    if hasattr(deriv_data[date_field], 'isoformat'):
                        deriv_data[date_field] = deriv_data[date_field].isoformat()
                    else:
                        deriv_data[date_field] = str(deriv_data[date_field])
            
            # Ensure JSONB fields are dicts
            for jsonb_field in ['metadata', 'engagement_metrics']:
                if jsonb_field in deriv_data and isinstance(deriv_data[jsonb_field], str):
                    try:
                        deriv_data[jsonb_field] = json.loads(deriv_data[jsonb_field])
                    except:
                        pass
            
            client.table('derivatives').upsert(deriv_data, on_conflict='id').execute()
        
        print(f"✅ Saved {len(derivatives)} derivatives to Supabase")
        return True
    except Exception as e:
        print(f"⚠️ Error saving derivatives to Supabase: {e}")
        import traceback
        traceback.print_exc()
        return False

# ==================== PILLARS ====================

def load_pillars_from_supabase(client_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load pillars from Supabase, optionally filtered by client_id"""
    client = get_supabase_client()
    if not client:
        return []
    
    try:
        query = client.table('pillars').select('*')
        if client_id:
            query = query.eq('client_id', client_id)
        response = query.order('created_at', desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"⚠️ Error loading pillars from Supabase: {e}")
        return []

def save_pillars_to_supabase(pillars: List[Dict[str, Any]]) -> bool:
    """Save pillars to Supabase (upsert)"""
    client = get_supabase_client()
    if not client:
        return False
    
    try:
        for pillar in pillars:
            pillar_data = pillar.copy()
            
            # Convert datetime strings
            for date_field in ['created_at', 'updated_at']:
                if date_field in pillar_data and not isinstance(pillar_data[date_field], str):
                    if hasattr(pillar_data[date_field], 'isoformat'):
                        pillar_data[date_field] = pillar_data[date_field].isoformat()
            
            # Ensure JSONB fields are dicts
            for jsonb_field in ['channels']:
                if jsonb_field in pillar_data and isinstance(pillar_data[jsonb_field], str):
                    try:
                        pillar_data[jsonb_field] = json.loads(pillar_data[jsonb_field])
                    except:
                        pass
            
            client.table('pillars').upsert(pillar_data, on_conflict='id').execute()
        
        print(f"✅ Saved {len(pillars)} pillars to Supabase")
        return True
    except Exception as e:
        print(f"⚠️ Error saving pillars to Supabase: {e}")
        return False

# ==================== METRICS ====================

def load_metrics_from_supabase(post_id: Optional[str] = None, pillar_id: Optional[str] = None) -> Dict[str, Any]:
    """Load metrics from Supabase"""
    client = get_supabase_client()
    if not client:
        return {"metrics": {}}
    
    try:
        query = client.table('content_metrics').select('*')
        if post_id:
            query = query.eq('post_id', post_id)
        if pillar_id:
            query = query.eq('pillar_id', pillar_id)
        response = query.order('recorded_at', desc=True).execute()
        metrics = response.data if response.data else []
        return {"metrics": metrics}
    except Exception as e:
        print(f"⚠️ Error loading metrics from Supabase: {e}")
        return {"metrics": {}}

def save_metrics_to_supabase(metrics: Dict[str, Any]) -> bool:
    """Save metrics to Supabase"""
    client = get_supabase_client()
    if not client:
        return False
    
    try:
        # Metrics structure might be different, adapt as needed
        # For now, just log that we're saving
        print("✅ Metrics saving not yet fully implemented")
        return True
    except Exception as e:
        print(f"⚠️ Error saving metrics to Supabase: {e}")
        return False

# ==================== CLIENTS ====================

def load_clients_from_supabase(user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load clients from Supabase, optionally filtered by user access"""
    client = get_supabase_client()
    if not client:
        return []
    
    try:
        if user_id:
            # Get clients accessible by this user
            user_clients_response = client.table('user_clients').select('client_id, role').eq('user_id', user_id).execute()
            accessible_client_ids = [uc['client_id'] for uc in (user_clients_response.data or [])]
            
            if not accessible_client_ids:
                return []
            
            # Load those clients
            response = client.table('clients').select('*').in_('client_id', accessible_client_ids).order('created_at', desc=True).execute()
            clients = response.data if response.data else []
            
            # Add user role to each client
            role_map = {uc['client_id']: uc['role'] for uc in (user_clients_response.data or [])}
            for client_data in clients:
                client_data['user_role'] = role_map.get(client_data['client_id'], 'viewer')
            
            return clients
        else:
            # Load all clients (admin mode)
            response = client.table('clients').select('*').order('created_at', desc=True).execute()
            return response.data if response.data else []
    except Exception as e:
        print(f"⚠️ Error loading clients from Supabase: {e}")
        import traceback
        traceback.print_exc()
        return []

def save_client_to_supabase(client_data: Dict[str, Any]) -> bool:
    """Save/update client in Supabase"""
    client = get_supabase_client()
    if not client:
        return False
    
    try:
        client_dict = client_data.copy()
        
        # Convert datetime strings
        for date_field in ['created_at', 'updated_at']:
            if date_field in client_dict and not isinstance(client_dict[date_field], str):
                if hasattr(client_dict[date_field], 'isoformat'):
                    client_dict[date_field] = client_dict[date_field].isoformat()
        
        # Ensure JSONB fields are dicts
        for jsonb_field in ['brand', 'funnel_structure', 'connected_accounts', 'metadata']:
            if jsonb_field in client_dict and isinstance(client_dict[jsonb_field], str):
                try:
                    client_dict[jsonb_field] = json.loads(client_dict[jsonb_field])
                except:
                    pass
        
        client.table('clients').upsert(client_dict, on_conflict='client_id').execute()
        print(f"✅ Saved client {client_dict.get('client_id')} to Supabase")
        return True
    except Exception as e:
        print(f"⚠️ Error saving client to Supabase: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_user_accessible_clients(user_id: str) -> List[str]:
    """Get list of client_ids accessible by user"""
    client = get_supabase_client()
    if not client:
        return []
    
    try:
        response = client.table('user_clients').select('client_id').eq('user_id', user_id).execute()
        return [uc['client_id'] for uc in (response.data or [])]
    except Exception as e:
        print(f"⚠️ Error getting user accessible clients: {e}")
        return []

def get_user_client_role(user_id: str, client_id: str) -> Optional[str]:
    """Get user's role for a specific client"""
    client = get_supabase_client()
    if not client:
        return None
    
    try:
        response = client.table('user_clients').select('role').eq('user_id', user_id).eq('client_id', client_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]['role']
        return None
    except Exception as e:
        print(f"⚠️ Error getting user client role: {e}")
        return None

# ==================== API CREDENTIALS ====================

def load_api_credentials_from_supabase(client_id: str, platform: Optional[str] = None) -> Dict[str, Any]:
    """Load API credentials from Supabase"""
    client = get_supabase_client()
    if not client:
        return {}
    
    try:
        query = client.table('api_credentials').select('*').eq('client_id', client_id)
        if platform:
            query = query.eq('platform', platform)
        response = query.execute()
        creds = response.data if response.data else []
        
        if platform and creds:
            return creds[0] if creds else {}
        return {c['platform']: c for c in creds}
    except Exception as e:
        print(f"⚠️ Error loading API credentials from Supabase: {e}")
        return {}

def save_api_credentials_to_supabase(client_id: str, platform: str, pub_id: Optional[str] = None, api_key: Optional[str] = None, metadata: Optional[Dict] = None) -> bool:
    """Save API credentials to Supabase"""
    client = get_supabase_client()
    if not client:
        return False
    
    try:
        cred_data = {
            'client_id': client_id,
            'platform': platform,
            'pub_id': pub_id,
            'api_key': api_key,
            'metadata': metadata or {}
        }
        
        client.table('api_credentials').upsert(cred_data, on_conflict='client_id,platform').execute()
        print(f"✅ Saved API credentials for {platform} to Supabase")
        return True
    except Exception as e:
        print(f"⚠️ Error saving API credentials to Supabase: {e}")
        return False


