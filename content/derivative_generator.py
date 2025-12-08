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

def load_derivatives():
    """Load all derivatives from JSON file"""
    if os.path.exists(CONTENT_DERIVATIVES_FILE):
        with open(CONTENT_DERIVATIVES_FILE, 'r') as f:
            return json.load(f)
    return {"derivatives": []}

def save_derivatives(data):
    """Save derivatives to JSON file"""
    with open(CONTENT_DERIVATIVES_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def generate_derivatives(post_id, include_podcast=False):
    """
    Generate all derivatives from center post
    
    Args:
        post_id: ID of the center post
        include_podcast: Whether to generate podcast (requires ElevenLabs)
    
    Returns:
        list: Generated derivatives
    """
    post = get_post(post_id)
    if not post:
        raise ValueError(f"Post {post_id} not found")
    
    # Prefer blog version, fallback to center post
    source_content = post.get('blog_version', {}).get('content') or \
                    post.get('center_post', {}).get('content', '')
    
    if not source_content:
        raise ValueError("Post must have content to generate derivatives")
    
    try:
        ai_client = ClaudeClient()
        derivatives = []
        data = load_derivatives()
        
        # 1. Generate Newsletter
        try:
            newsletter_result = ai_client.generate_newsletter_version(source_content)
            deriv_id = f"deriv_{uuid.uuid4().hex[:12]}"
            derivative = {
                "id": deriv_id,
                "post_id": post_id,
                "type": "newsletter",
                "content": newsletter_result.get('content', ''),
                "metadata": {
                    "subject": newsletter_result.get('subject', ''),
                    "platform": "beehiiv",
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
            print(f"Warning: Failed to generate newsletter: {e}")
        
        # 2. Generate Telegram announcement
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
            print(f"Warning: Failed to generate Telegram announcement: {e}")
        
        # 3. Generate Social Posts
        try:
            social_posts = ai_client.generate_social_posts(source_content, ['x', 'linkedin', 'instagram'])
            
            # Process X posts
            for i, x_post in enumerate(social_posts.get('x', []), 1):
                deriv_id = f"deriv_{uuid.uuid4().hex[:12]}"
                derivative = {
                    "id": deriv_id,
                    "post_id": post_id,
                    "type": "social_x",
                    "content": x_post.get('content', ''),
                    "metadata": {
                        "platform": "x",
                        "post_number": i,
                        "post_type": x_post.get('type', 'single_post'),
                        "thread_parts": x_post.get('thread_parts', []),
                        "status": "queued"
                    },
                    "created_at": datetime.now().isoformat(),
                    "scheduled_for": None,
                    "published_at": None,
                    "engagement_metrics": {}
                }
                derivatives.append(derivative)
                data['derivatives'].append(derivative)
            
            # Process LinkedIn post
            for linkedin_post in social_posts.get('linkedin', []):
                deriv_id = f"deriv_{uuid.uuid4().hex[:12]}"
                derivative = {
                    "id": deriv_id,
                    "post_id": post_id,
                    "type": "social_linkedin",
                    "content": linkedin_post.get('content', ''),
                    "metadata": {
                        "platform": "linkedin",
                        "post_type": linkedin_post.get('type', 'single_post'),
                        "status": "queued"
                    },
                    "created_at": datetime.now().isoformat(),
                    "scheduled_for": None,
                    "published_at": None,
                    "engagement_metrics": {}
                }
                derivatives.append(derivative)
                data['derivatives'].append(derivative)
            
            # Process Instagram carousel
            for ig_post in social_posts.get('instagram', []):
                deriv_id = f"deriv_{uuid.uuid4().hex[:12]}"
                derivative = {
                    "id": deriv_id,
                    "post_id": post_id,
                    "type": "social_ig",
                    "content": ig_post.get('content', ''),
                    "metadata": {
                        "platform": "instagram",
                        "post_type": "carousel",
                        "slides": ig_post.get('slides', []),
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
    data = load_derivatives()
    derivatives = data.get('derivatives', [])
    
    if post_id:
        derivatives = [d for d in derivatives if d.get('post_id') == post_id]
    
    if status:
        derivatives = [d for d in derivatives if d.get('metadata', {}).get('status') == status]
    
    return derivatives

