"""
Generate archive and blog versions from center post
"""
from datetime import datetime
from .center_post import get_post, update_post
from .ai_client import ClaudeClient

def generate_branches(post_id):
    """
    Generate archive and blog versions from center post
    
    Args:
        post_id: ID of the center post
    
    Returns:
        dict: Updated post with branches
    """
    post = get_post(post_id)
    if not post:
        raise ValueError(f"Post {post_id} not found")
    
    if not post.get('center_post'):
        raise ValueError("Post must have center_post content to generate branches")
    
    center_content = post['center_post'].get('content', '')
    
    try:
        ai_client = ClaudeClient()
        
        # Generate archive version (narrative, personal)
        archive_content = ai_client.generate_archive_version(center_content)
        
        # Get current chapter number (count existing archive posts)
        from .center_post import load_content_posts
        data = load_content_posts()
        archive_count = sum(1 for p in data['posts'] if p.get('archive_version'))
        chapter_number = archive_count + 1
        
        # Generate blog version (AI-optimized)
        blog_result = ai_client.generate_blog_version(center_content)
        
        # Update post with branches
        updates = {
            'archive_version': {
                'content': archive_content,
                'chapter_number': chapter_number,
                'generated_at': datetime.now().isoformat()
            },
            'blog_version': {
                'content': blog_result.get('content', ''),
                'structured_data': blog_result.get('structured_data', {}),
                'generated_at': datetime.now().isoformat()
            },
            'status': 'branched'
        }
        
        updated_post = update_post(post_id, updates)
        return updated_post
        
    except Exception as e:
        raise Exception(f"Error generating branches: {str(e)}")

