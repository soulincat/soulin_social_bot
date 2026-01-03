"""
Generate derivatives (podcast, newsletter, social posts) from center post
"""
import json
import os
import uuid
from datetime import datetime
from .center_post import get_post
from .ai_client import ClaudeClient

CONTENT_DERIVATIVES_FILE = 'content_derivatives.json'

# In-memory cache for derivatives created during session (fallback)
_in_memory_derivatives = {}

def load_derivatives(post_id=None):
    """Load all derivatives from Supabase, KV, file, or memory cache"""
    # Try Supabase first (recommended)
    try:
        from .supabase_storage import load_derivatives_from_supabase
        supabase_data = load_derivatives_from_supabase(post_id=post_id)
        if supabase_data and supabase_data.get('derivatives'):
            # Merge with in-memory cache
            all_derivatives = {deriv['id']: deriv for deriv in supabase_data.get('derivatives', [])}
            all_derivatives.update(_in_memory_derivatives)
            return {"derivatives": list(all_derivatives.values())}
    except Exception as e:
        print(f"⚠️ Supabase not available: {e}")
    
    # Fallback to KV (for Vercel without Supabase)
    try:
        from .storage import load_derivatives
        kv_data = load_derivatives()
        if kv_data:
            # Filter by post_id if needed
            derivatives = kv_data.get('derivatives', [])
            if post_id:
                derivatives = [d for d in derivatives if d.get('post_id') == post_id]
            # Merge with in-memory cache
            all_derivatives = {deriv['id']: deriv for deriv in derivatives}
            all_derivatives.update(_in_memory_derivatives)
            return {"derivatives": list(all_derivatives.values())}
    except Exception as e:
        print(f"⚠️ KV not available: {e}")
    
    # Fallback to file (for local development)
    file_derivatives = []
    if os.path.exists(CONTENT_DERIVATIVES_FILE):
        try:
            with open(CONTENT_DERIVATIVES_FILE, 'r') as f:
                file_data = json.load(f)
                file_derivatives = file_data.get('derivatives', [])
                if post_id:
                    file_derivatives = [d for d in file_derivatives if d.get('post_id') == post_id]
        except Exception as e:
            print(f"⚠️ Warning: Could not load {CONTENT_DERIVATIVES_FILE}: {e}")
    
    # Merge with in-memory derivatives (in-memory takes precedence)
    all_derivatives = {deriv['id']: deriv for deriv in file_derivatives}
    all_derivatives.update(_in_memory_derivatives)
    
    return {"derivatives": list(all_derivatives.values())}

def save_derivatives(data):
    """Save derivatives to Supabase, KV, file, or memory cache"""
    # Update in-memory cache
    global _in_memory_derivatives
    derivatives = data.get('derivatives', [])
    for deriv in derivatives:
        _in_memory_derivatives[deriv['id']] = deriv
    
    # Try Supabase first (recommended)
    supabase_saved = False
    try:
        from .supabase_storage import save_derivatives_to_supabase
        if save_derivatives_to_supabase(derivatives):
            print("✅ Saved derivatives to Supabase")
            supabase_saved = True
    except Exception as e:
        print(f"⚠️ Supabase save failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Fallback to KV (for Vercel without Supabase)
    if not supabase_saved:
        kv_saved = False
        try:
            from .storage import save_derivatives
            if save_derivatives(data):
                print("✅ Saved derivatives to Vercel KV")
                kv_saved = True
        except Exception as e:
            print(f"⚠️ KV not available: {e}")
        
        # Fallback to file (for local development)
        if not kv_saved:
            try:
                with open(CONTENT_DERIVATIVES_FILE, 'w') as f:
                    json.dump(data, f, indent=2)
                print("✅ Saved derivatives to file")
            except (OSError, PermissionError) as e:
                # Handle read-only filesystem (e.g., on Vercel without storage)
                print(f"⚠️ Warning: Could not save to {CONTENT_DERIVATIVES_FILE}: {e}")
                print("   This is expected on read-only filesystems (e.g., Vercel).")
                print("   Derivative data is cached in memory for this session only.")
                print("   To persist data, set up Supabase or Vercel KV.")
                # Don't raise - allow the function to continue

def update_derivative(deriv_id, updates):
    """Update a derivative with new data"""
    data = load_derivatives()
    for derivative in data['derivatives']:
        if derivative['id'] == deriv_id:
            derivative.update(updates)
            derivative['updated_at'] = datetime.now().isoformat()
            save_derivatives(data)
            return derivative
    raise ValueError(f"Derivative {deriv_id} not found")

def generate_derivatives(post_id, include_podcast=False, platforms=None, client_id=None):
    """
    Generate derivatives from center post for selected platforms
    
    Args:
        post_id: ID of the center post
        include_podcast: Whether to generate podcast (requires ElevenLabs)
        platforms: List of platforms to generate for (default: all)
        client_id: Optional client ID to load brand social settings
    
    Returns:
        list: Generated derivatives
    """
    if platforms is None:
        platforms = ['linkedin', 'x', 'threads', 'instagram', 'substack', 'telegram']
    post = get_post(post_id)
    if not post:
        raise ValueError(f"Post {post_id} not found")
    
    # Get client_id from post if not provided
    if not client_id:
        client_id = post.get('client_id')
    
    # Load brand social settings and main_product CTA if client_id available
    brand_socials = {}
    cta_info = None
    if client_id:
        try:
            import json
            import os
            if os.path.exists('clients.json'):
                with open('clients.json', 'r') as f:
                    clients_data = json.load(f)
                    for client in clients_data.get('clients', []):
                        if client.get('client_id') == client_id:
                            brand_socials = client.get('brand', {}).get('socials', {})
                            # Get CTA info if post has include_cta flag
                            if post.get('include_cta'):
                                main_product = client.get('brand', {}).get('main_product', {})
                                if main_product.get('cta_text') and main_product.get('cta_url'):
                                    cta_info = {
                                        'text': main_product['cta_text'],
                                        'url': main_product['cta_url']
                                    }
                            break
        except Exception as e:
            print(f"Warning: Could not load brand social settings: {e}")
    
    # Prefer blog version, fallback to center post
    source_content = post.get('blog_version', {}).get('content') or \
                    post.get('center_post', {}).get('content', '')
    
    if not source_content:
        raise ValueError("Post must have content to generate derivatives")
    
    try:
        ai_client = ClaudeClient()
        derivatives = []
        data = load_derivatives()
        
        # 1. Center Post = Newsletter (only create if newsletter not already exists)
        # Check if newsletter already exists for this post
        existing_newsletter = [d for d in data.get('derivatives', []) 
                              if d.get('post_id') == post_id and d.get('type') == 'newsletter']
        
        if not existing_newsletter:
            try:
                deriv_id = f"deriv_{uuid.uuid4().hex[:12]}"
                derivative = {
                    "id": deriv_id,
                    "post_id": post_id,
                    "type": "newsletter",
                    "content": source_content,  # Use center post as newsletter
                    "metadata": {
                        "subject": post.get('center_post', {}).get('title', ''),
                        "platform": "beehiiv",
                        "status": "draft"
                    },
                    "created_at": datetime.now().isoformat(),
                    "scheduled_for": None,
                    "published_at": None,
                    "engagement_metrics": {}
                }
                derivatives.append(derivative)
                data['derivatives'].append(derivative)
            except Exception as e:
                print(f"Warning: Failed to create newsletter: {e}")
        
        # 2. Generate Telegram announcement (if selected)
        if 'telegram' in platforms:
            try:
                telegram_content = ai_client.generate_telegram_announcement(source_content)
                deriv_id = f"deriv_{uuid.uuid4().hex[:12]}"
                derivative = {
                    "id": deriv_id,
                    "post_id": post_id,
                    "type": "telegram",
                    "content": telegram_content,
                    "metadata": {
                        "platform": "telegram",
                        "status": "draft"
                    },
                    "created_at": datetime.now().isoformat(),
                    "scheduled_for": None,
                    "published_at": None,
                    "engagement_metrics": {}
                }
                derivatives.append(derivative)
                data['derivatives'].append(derivative)
            except Exception as e:
                print(f"Warning: Failed to generate Telegram announcement: {e}")
        
        # 3. Generate Social Posts (Socials) - only for selected platforms
        social_platforms = [p for p in platforms if p in ['linkedin', 'x', 'threads', 'instagram', 'substack']]
        if social_platforms:
            try:
                # Pass brand social settings and CTA info to AI client
                social_posts = ai_client.generate_social_posts(
                    source_content, 
                    social_platforms,
                    brand_socials=brand_socials,
                    cta_info=cta_info
                )
                
                # Get post count per platform from brand settings
                def get_post_count(platform):
                    if brand_socials and platform in brand_socials:
                        return brand_socials[platform].get('postCount', 1)
                    return 1  # Default to 1 post
                
                # Process LinkedIn posts
                linkedin_posts = social_posts.get('linkedin', [])
                linkedin_posts = linkedin_posts[:get_post_count('linkedin')]
                for i, linkedin_post in enumerate(linkedin_posts, 1):
                    deriv_id = f"deriv_{uuid.uuid4().hex[:12]}"
                    derivative = {
                        "id": deriv_id,
                        "post_id": post_id,
                        "type": "linkedin",
                        "content": linkedin_post.get('content', ''),
                        "metadata": {
                            "platform": "linkedin",
                            "post_number": i,
                            "post_type": linkedin_post.get('type', 'single_post'),
                            "status": "draft"
                        },
                        "created_at": datetime.now().isoformat(),
                        "scheduled_for": None,
                        "published_at": None,
                        "engagement_metrics": {}
                    }
                    derivatives.append(derivative)
                    data['derivatives'].append(derivative)
                
                # Process X (Twitter) posts
                x_posts = social_posts.get('x', [])
                x_posts = x_posts[:get_post_count('x')]
                for i, x_post in enumerate(x_posts, 1):
                    deriv_id = f"deriv_{uuid.uuid4().hex[:12]}"
                    content = x_post.get('content', '')
                    if x_post.get('type') == 'thread' and x_post.get('thread_parts'):
                        content = '\n\n---\n\n'.join(x_post.get('thread_parts', []))
                    
                    derivative = {
                        "id": deriv_id,
                        "post_id": post_id,
                        "type": "x",
                        "content": content,
                        "metadata": {
                            "platform": "x",
                            "post_number": i,
                            "post_type": x_post.get('type', 'single_post'),
                            "thread_parts": x_post.get('thread_parts', []),
                            "status": "draft"
                        },
                        "created_at": datetime.now().isoformat(),
                        "scheduled_for": None,
                        "published_at": None,
                        "engagement_metrics": {}
                    }
                    derivatives.append(derivative)
                    data['derivatives'].append(derivative)
                
                # Process Threads posts
                threads_posts = social_posts.get('threads', [])
                threads_posts = threads_posts[:get_post_count('threads')]
                for i, threads_post in enumerate(threads_posts, 1):
                    deriv_id = f"deriv_{uuid.uuid4().hex[:12]}"
                    content = threads_post.get('content', '')
                    if threads_post.get('type') == 'thread' and threads_post.get('thread_parts'):
                        content = '\n\n---\n\n'.join(threads_post.get('thread_parts', []))
                    
                    derivative = {
                        "id": deriv_id,
                        "post_id": post_id,
                        "type": "threads",
                        "content": content,
                        "metadata": {
                            "platform": "threads",
                            "post_number": i,
                            "post_type": threads_post.get('type', 'single_post'),
                            "thread_parts": threads_post.get('thread_parts', []),
                            "status": "draft"
                        },
                        "created_at": datetime.now().isoformat(),
                        "scheduled_for": None,
                        "published_at": None,
                        "engagement_metrics": {}
                    }
                    derivatives.append(derivative)
                    data['derivatives'].append(derivative)
                
                # Process Instagram carousel
                instagram_posts = social_posts.get('instagram', [])
                instagram_posts = instagram_posts[:get_post_count('instagram')]
                for ig_post in instagram_posts:
                    deriv_id = f"deriv_{uuid.uuid4().hex[:12]}"
                    slides = ig_post.get('slides', [])
                    content = ig_post.get('content', '')
                    if slides:
                        content += '\n\n--- CAROUSEL SLIDES ---\n\n'
                        content += '\n\n---\n\n'.join([f"Slide {i+1}: {slide}" for i, slide in enumerate(slides)])
                    
                    derivative = {
                        "id": deriv_id,
                        "post_id": post_id,
                        "type": "instagram",
                        "content": content,
                        "metadata": {
                            "platform": "instagram",
                            "post_type": "carousel",
                            "slides": slides,
                            "status": "draft"
                        },
                        "created_at": datetime.now().isoformat(),
                        "scheduled_for": None,
                        "published_at": None,
                        "engagement_metrics": {}
                    }
                    derivatives.append(derivative)
                    data['derivatives'].append(derivative)
                
                # Process Substack feed posts
                substack_posts = social_posts.get('substack', [])
                substack_posts = substack_posts[:get_post_count('substack')]
                for i, substack_post in enumerate(substack_posts, 1):
                    deriv_id = f"deriv_{uuid.uuid4().hex[:12]}"
                    derivative = {
                        "id": deriv_id,
                        "post_id": post_id,
                        "type": "substack",
                        "content": substack_post.get('content', ''),
                        "metadata": {
                            "platform": "substack",
                            "post_number": i,
                            "post_type": substack_post.get('type', 'feed_post'),
                            "status": "draft"
                        },
                        "created_at": datetime.now().isoformat(),
                        "scheduled_for": None,
                        "published_at": None,
                        "engagement_metrics": {}
                    }
                    derivatives.append(derivative)
                    data['derivatives'].append(derivative)
            except Exception as e:
                print(f"Warning: Failed to generate social posts: {e}")
        
        # 4. Generate Podcast (optional, requires ElevenLabs)
        if include_podcast:
            try:
                # For now, just create placeholder
                # Full implementation would use ElevenLabs API
                deriv_id = f"deriv_{uuid.uuid4().hex[:12]}"
                derivative = {
                    "id": deriv_id,
                    "post_id": post_id,
                    "type": "podcast",
                    "content": source_content,  # Will be converted to audio
                    "metadata": {
                        "platform": "podcast",
                        "audio_url": None,
                        "status": "queued"
                    },
                    "created_at": datetime.now().isoformat(),
                    "scheduled_for": None,
                    "published_at": None,
                    "engagement_metrics": {}
                }
                derivatives.append(derivative)
                data['derivatives'].append(derivative)
            except Exception as e:
                print(f"Warning: Failed to generate podcast: {e}")
        
        save_derivatives(data)
        return derivatives
        
    except Exception as e:
        raise Exception(f"Error generating derivatives: {str(e)}")

def get_derivatives(post_id=None, status=None):
    """Get derivatives, optionally filtered by post_id or status"""
    data = load_derivatives(post_id=post_id)  # Pass post_id to load_derivatives for efficient filtering
    derivatives = data.get('derivatives', [])
    
    # Additional filtering by status if needed
    if status:
        derivatives = [d for d in derivatives if d.get('metadata', {}).get('status') == status]
    
    return derivatives

