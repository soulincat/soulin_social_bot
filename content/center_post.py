"""
Center post creation and validation
"""
import json
import os
import uuid
from datetime import datetime
from .ai_client import ClaudeClient

CONTENT_POSTS_FILE = 'content_posts.json'

# In-memory cache for posts created during session (fallback)
_in_memory_posts = {}

def load_content_posts():
    """Load all content posts from KV, file, or memory cache"""
    # Try KV first (for Vercel)
    try:
        from .storage import load_posts
        kv_data = load_posts()
        if kv_data:
            # Merge with in-memory cache
            all_posts = {post['id']: post for post in kv_data.get('posts', [])}
            all_posts.update(_in_memory_posts)
            return {"posts": list(all_posts.values())}
    except Exception as e:
        print(f"⚠️ KV not available: {e}")
    
    # Fallback to file
    file_posts = []
    if os.path.exists(CONTENT_POSTS_FILE):
        try:
            with open(CONTENT_POSTS_FILE, 'r') as f:
                file_data = json.load(f)
                file_posts = file_data.get('posts', [])
        except Exception as e:
            print(f"⚠️ Warning: Could not load {CONTENT_POSTS_FILE}: {e}")
    
    # Merge with in-memory posts (in-memory takes precedence)
    all_posts = {post['id']: post for post in file_posts}
    all_posts.update(_in_memory_posts)
    
    return {"posts": list(all_posts.values())}

def save_content_posts(data):
    """Save content posts to KV, file, or memory cache"""
    # Update in-memory cache
    global _in_memory_posts
    for post in data.get('posts', []):
        _in_memory_posts[post['id']] = post
    
    # Try KV first (for Vercel)
    try:
        from .storage import save_posts
        if save_posts(data):
            print("✅ Saved posts to Vercel KV")
            return
    except Exception as e:
        print(f"⚠️ KV not available: {e}")
    
    # Fallback to file
    try:
        with open(CONTENT_POSTS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print("✅ Saved posts to file")
    except (OSError, PermissionError) as e:
        # Handle read-only filesystem (e.g., on Vercel without KV)
        print(f"⚠️ Warning: Could not save to {CONTENT_POSTS_FILE}: {e}")
        print("   Post data is cached in memory for this session only.")
        print("   To persist data, set up Vercel KV in your Vercel project settings.")
        # Don't raise - allow the function to continue

def create_center_post(client_id, raw_idea, auto_expand=True, pillar_id=None, include_cta=False):
    """
    Create center post from raw idea
    
    Args:
        client_id: Client identifier
        raw_idea: Raw idea text
        auto_expand: If True, use AI to expand immediately
        pillar_id: Optional pillar ID to assign
        include_cta: If True, include main product CTA in generated content
    
    Returns:
        dict: Created post data
    """
    # Load client config - handle missing file gracefully
    try:
        with open('clients.json', 'r') as f:
            clients_data = json.load(f)
    except FileNotFoundError:
        print(f"⚠️ clients.json not found, using dummy client for {client_id}")
        clients_data = {"clients": []}
    
    client = None
    for c in clients_data.get('clients', []):
        if c.get('client_id') == client_id:
            client = c
            break
    
    # If client not found, create a minimal client structure
    if not client:
        print(f"⚠️ Client {client_id} not found in clients.json, using minimal client structure")
        client = {
            'client_id': client_id,
            'brand': {}
        }
    
    # Create post structure
    post_id = f"post_{uuid.uuid4().hex[:12]}"
    post = {
        "id": post_id,
        "created_at": datetime.now().isoformat(),
        "client_id": client_id,
        "status": "idea",  # Start as "idea"
        "raw_idea": raw_idea,
        "pillar_id": pillar_id,
        "include_cta": include_cta,
        "time_invested_minutes": 0
    }
    
    if auto_expand:
        try:
            # Load existing posts
            data = load_content_posts()
            
            # Expand with AI
            ai_client = ClaudeClient()
            # Get main_product CTA if include_cta is True
            cta_info = None
            if include_cta:
                main_product = client.get('brand', {}).get('main_product', {})
                if main_product.get('cta_text') and main_product.get('cta_url'):
                    cta_info = {
                        'text': main_product['cta_text'],
                        'url': main_product['cta_url']
                    }
            expanded = ai_client.expand_idea(raw_idea, client, cta_info=cta_info)
            
            # Calculate word count
            word_count = len(expanded.get('content', '').split())
            
            post['center_post'] = {
                "title": expanded.get('title', ''),
                "content": expanded.get('content', ''),
                "word_count": expanded.get('word_count', word_count),
                "checks": expanded.get('checks', {})
            }
            post['status'] = 'drafted'  # After AI expansion, status becomes "drafted"
            
            # Save
            data['posts'].append(post)
            save_content_posts(data)
            
            return post
        except Exception as e:
            # Save as idea even if AI fails - don't raise, just return the post
            post['status'] = 'idea'
            post['error'] = str(e)
            data = load_content_posts()
            data['posts'].append(post)
            save_content_posts(data)
            # Return the post instead of raising - frontend can handle it
            print(f"⚠️ AI expansion failed: {str(e)}")
            print("   Post saved as 'idea' status. User can expand manually later.")
            return post
    else:
        # Just save raw idea
        data = load_content_posts()
        data['posts'].append(post)
        save_content_posts(data)
        return post

def get_post(post_id):
    """Get a specific post by ID"""
    data = load_content_posts()
    for post in data['posts']:
        if post['id'] == post_id:
            return post
    return None

def list_posts(client_id=None, status=None):
    """List all posts, optionally filtered by client or status"""
    data = load_content_posts()
    posts = data.get('posts', [])
    
    if client_id:
        posts = [p for p in posts if p.get('client_id') == client_id]
    
    if status:
        posts = [p for p in posts if p.get('status') == status]
    
    # Sort by created_at descending
    posts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return posts

def update_post(post_id, updates):
    """Update a post with new data"""
    data = load_content_posts()
    for post in data['posts']:
        if post['id'] == post_id:
            post.update(updates)
            post['updated_at'] = datetime.now().isoformat()
            save_content_posts(data)
            return post
    raise ValueError(f"Post {post_id} not found")

def delete_post(post_id):
    """Delete a post"""
    data = load_content_posts()
    data['posts'] = [p for p in data['posts'] if p['id'] != post_id]
    save_content_posts(data)

