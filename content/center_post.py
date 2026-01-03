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
    """Load all content posts from Supabase, KV, file, or memory cache"""
    # Try Supabase first (recommended)
    try:
        from .supabase_storage import load_posts_from_supabase
        supabase_data = load_posts_from_supabase()
        if supabase_data and supabase_data.get('posts'):
            # Merge with in-memory cache (in-memory takes precedence for current session)
            all_posts = {post['id']: post for post in supabase_data.get('posts', [])}
            all_posts.update(_in_memory_posts)
            return {"posts": list(all_posts.values())}
    except Exception as e:
        print(f"⚠️ Supabase not available: {e}")
    
    # Fallback to KV (for Vercel without Supabase)
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
    
    # Fallback to file (for local development)
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
    """Save content posts to Supabase, KV, file, or memory cache"""
    # Update in-memory cache (for current session)
    global _in_memory_posts
    posts = data.get('posts', [])
    for post in posts:
        _in_memory_posts[post['id']] = post
    
    # Try Supabase first (recommended)
    supabase_saved = False
    try:
        from .supabase_storage import save_posts_to_supabase
        if save_posts_to_supabase(posts):
            print("✅ Saved posts to Supabase")
            supabase_saved = True
    except Exception as e:
        print(f"⚠️ Supabase save failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Fallback to KV (for Vercel without Supabase)
    if not supabase_saved:
        kv_saved = False
        try:
            from .storage import save_posts
            if save_posts(data):
                print("✅ Saved posts to Vercel KV")
                kv_saved = True
        except Exception as e:
            print(f"⚠️ KV save failed: {e}")
        
        # Fallback to file (for local development)
        if not kv_saved:
            try:
                with open(CONTENT_POSTS_FILE, 'w') as f:
                    json.dump(data, f, indent=2)
                print("✅ Saved posts to file")
            except (OSError, PermissionError) as e:
                # Handle read-only filesystem (e.g., on Vercel without storage)
                print(f"⚠️ WARNING: Could not save to {CONTENT_POSTS_FILE}: {e}")
                print("   ⚠️ CRITICAL: Post data is ONLY in memory cache and will be LOST after this request!")
                print("   ⚠️ Set up Supabase or Vercel KV to persist data.")
                # Don't raise - allow the function to continue, but warn loudly

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
            post['status'] = 'idea'  # Always 'idea' when AI expansion fails
            error_msg = str(e)
            post['error'] = error_msg
            # Don't add center_post when AI fails
            data = load_content_posts()
            data['posts'].append(post)
            save_content_posts(data)
            # Return the post instead of raising - frontend can handle it
            print(f"⚠️ AI expansion failed: {error_msg}")
            print("   Post saved as 'idea' status without center_post.")
            print("   User can expand manually later or fix API key and try again.")
            # Log specific error types for debugging
            if "ANTHROPIC_API_KEY" in error_msg:
                print("   🔑 Issue: ANTHROPIC_API_KEY missing or invalid")
            elif "401" in error_msg or "authentication" in error_msg.lower():
                print("   🔑 Issue: Invalid API key (authentication failed)")
            elif "404" in error_msg or "not_found" in error_msg.lower():
                print("   🤖 Issue: Model not found (check ANTHROPIC_MODEL setting)")
            elif "JSON" in error_msg or "parsing" in error_msg.lower():
                print("   📄 Issue: Claude returned invalid JSON format")
                print(f"   Full error: {error_msg[:500]}")
            return post
    else:
        # Just save raw idea
        data = load_content_posts()
        data['posts'].append(post)
        save_content_posts(data)
        return post

def get_post(post_id):
    """Get a specific post by ID"""
    # Try Supabase first for direct lookup
    try:
        from .supabase_storage import get_post_from_supabase
        post = get_post_from_supabase(post_id)
        if post:
            print(f"✅ Found post in Supabase: {post_id}")
            return post
    except Exception as e:
        print(f"⚠️ Supabase lookup failed: {e}")
    
    # Fallback to loading all posts
    data = load_content_posts()
    posts = data.get('posts', [])
    print(f"🔍 Looking for post_id: {post_id}")
    print(f"📊 Total posts loaded: {len(posts)}")
    for post in posts:
        if post.get('id') == post_id:
            print(f"✅ Found post: {post_id}")
            return post
    print(f"❌ Post not found: {post_id}")
    print(f"Available post IDs: {[p.get('id') for p in posts[:5]]}")
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

