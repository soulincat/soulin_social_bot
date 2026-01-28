"""
Publishing system for derivatives
"""
import os
import json
from datetime import datetime
from .derivative_generator import load_derivatives, save_derivatives, get_derivatives
from dotenv import load_dotenv

load_dotenv()

def schedule_derivatives(post_id, schedule_config):
    """
    Schedule derivatives for publishing
    Changes status from 'approved' to 'queued' when scheduled
    
    Args:
        post_id: ID of the center post
        schedule_config: Dict with scheduling info
            {
                "blog_publish_at": "2025-01-15T10:00:00Z",
                "newsletter_send_at": "2025-01-15T12:00:00Z",
                "telegram_send_at": "2025-01-15T12:00:00Z",
                "social_stagger_hours": 24
            }
    """
    # Get approved derivatives (they become queued when scheduled)
    derivatives = get_derivatives(post_id=post_id, status='approved')
    
    if not derivatives:
        raise ValueError(f"No approved derivatives found for post {post_id}")
    
    data = load_derivatives()
    
    for derivative in derivatives:
        deriv_type = derivative.get('type')
        
        # Set scheduled_for based on type
        scheduled_time = None
        if deriv_type == 'newsletter' and schedule_config.get('newsletter_send_at'):
            scheduled_time = schedule_config['newsletter_send_at']
        elif deriv_type == 'telegram' and schedule_config.get('telegram_send_at'):
            scheduled_time = schedule_config['telegram_send_at']
        elif deriv_type in ['linkedin', 'x', 'threads', 'instagram', 'substack']:
            # Stagger social posts
            base_time = schedule_config.get('social_start_at', schedule_config.get('newsletter_send_at'))
            if base_time:
                from datetime import datetime, timedelta
                base_dt = datetime.fromisoformat(base_time.replace('Z', '+00:00'))
                post_num = (derivative.get('metadata') or {}).get('post_number', 1)
                stagger_hours = schedule_config.get('social_stagger_hours', 24)
                scheduled_dt = base_dt + timedelta(hours=(post_num - 1) * stagger_hours)
                scheduled_time = scheduled_dt.isoformat()
        
        # Update in data
        for d in data['derivatives']:
            if d['id'] == derivative['id']:
                if scheduled_time:
                    d['scheduled_for'] = scheduled_time
                    d['metadata']['status'] = 'queued'  # Change from approved to queued
                break
    
    save_derivatives(data)
    return derivatives

def get_beehiiv_credentials(client_id):
    """
    Get Beehiiv publication ID and API key for a client
    
    Returns:
        tuple: (pub_id, api_key) or (None, None) if not configured
    """
    import json
    
    try:
        with open('clients.json', 'r') as f:
            clients_data = json.load(f)
    except FileNotFoundError:
        print(f"⚠️ clients.json not found, cannot get Beehiiv credentials")
        return None
    
    client = None
    for c in clients_data.get('clients', []):
        if c.get('client_id') == client_id:
            client = c
            break
    
    if not client:
        return None, None
    
    # Try new structure first: funnel_structure.capture.api_connection
    funnel_structure = client.get('funnel_structure', {})
    capture_config = funnel_structure.get('capture', {})
    api_connection = capture_config.get('api_connection', {})
    
    if api_connection.get('type') == 'beehiiv':
        pub_id = api_connection.get('pub_id')
        api_key = api_connection.get('api_key')
        
        # If api_key is "env_var", get from environment
        if api_key == 'env_var' or not api_key:
            api_key = os.getenv('BEEHIIV_API_KEY')
        
        # If pub_id is "env_var", we can't proceed
        if pub_id == 'env_var' or not pub_id:
            pub_id = None
        
        if pub_id and api_key:
            return pub_id, api_key
    
    # Fall back to legacy structure
    if client.get('beehiiv_pub_id') and client['beehiiv_pub_id'] != 'your_beehiiv_pub_id':
        pub_id = client['beehiiv_pub_id']
        api_key = os.getenv('BEEHIIV_API_KEY')
        if api_key:
            return pub_id, api_key
    
    return None, None

def convert_content_to_beehiiv_blocks(content):
    """
    Convert newsletter content (markdown/text) to Beehiiv blocks format
    
    Beehiiv blocks format:
    [
        {
            "type": "text",
            "content": "Your text content here"
        },
        {
            "type": "heading",
            "level": 2,
            "content": "Heading text"
        }
    ]
    """
    import re
    
    blocks = []
    lines = content.split('\n')
    current_paragraph = []
    
    for line in lines:
        line = line.strip()
        
        if not line:
            # Empty line - flush current paragraph
            if current_paragraph:
                blocks.append({
                    "type": "text",
                    "content": '\n'.join(current_paragraph)
                })
                current_paragraph = []
            continue
        
        # Check for headings
        if line.startswith('#'):
            # Flush current paragraph first
            if current_paragraph:
                blocks.append({
                    "type": "text",
                    "content": '\n'.join(current_paragraph)
                })
                current_paragraph = []
            
            # Count # to determine level
            level = len(line) - len(line.lstrip('#'))
            heading_text = line.lstrip('#').strip()
            
            if heading_text:
                blocks.append({
                    "type": "heading",
                    "level": min(level, 3),  # Beehiiv supports 1-3
                    "content": heading_text
                })
        # Check for bold/italic (markdown)
        elif line.startswith('**') and line.endswith('**'):
            # Flush current paragraph
            if current_paragraph:
                blocks.append({
                    "type": "text",
                    "content": '\n'.join(current_paragraph)
                })
                current_paragraph = []
            
            # Bold text
            bold_text = line.strip('*').strip()
            blocks.append({
                "type": "text",
                "content": bold_text,
                "bold": True
            })
        # Check for lists
        elif line.startswith('- ') or line.startswith('* ') or re.match(r'^\d+\.', line):
            # Flush current paragraph
            if current_paragraph:
                blocks.append({
                    "type": "text",
                    "content": '\n'.join(current_paragraph)
                })
                current_paragraph = []
            
            # List item
            list_text = re.sub(r'^[-*\d+\.]\s*', '', line)
            blocks.append({
                "type": "text",
                "content": f"• {list_text}"
            })
        else:
            # Regular text - accumulate into paragraph
            current_paragraph.append(line)
    
    # Flush remaining paragraph
    if current_paragraph:
        blocks.append({
            "type": "text",
            "content": '\n'.join(current_paragraph)
        })
    
    # If no blocks created, create one with all content
    if not blocks:
        blocks.append({
            "type": "text",
            "content": content
        })
    
    return blocks

def publish_to_beehiiv(derivative, client_id=None):
    """
    Publish newsletter to Beehiiv using Send API
    
    Args:
        derivative: Derivative dict with content and metadata
        client_id: Client ID to get Beehiiv credentials
    
    Returns:
        dict: {
            'success': bool,
            'published_url': str or None,
            'post_id': str or None,
            'message': str
        }
    """
    import requests
    
    # Get client_id from post if not provided
    if not client_id:
        from .center_post import get_post
        post_id = derivative.get('post_id')
        if post_id:
            post = get_post(post_id)
            if post:
                client_id = post.get('client_id')
    
    if not client_id:
        return {
            'success': False,
            'published_url': None,
            'post_id': None,
            'message': 'Client ID not found'
        }
    
    # Get Beehiiv credentials
    pub_id, api_key = get_beehiiv_credentials(client_id)
    
    if not pub_id or not api_key:
        return {
            'success': False,
            'published_url': None,
            'post_id': None,
            'message': 'Beehiiv credentials not configured. Please set BEEHIIV_API_KEY and pub_id in client config.'
        }
    
    # Get content and subject
    content = derivative.get('content', '')
    metadata = derivative.get('metadata', {})
    subject = metadata.get('subject', 'Untitled Newsletter')
    
    if not content:
        return {
            'success': False,
            'published_url': None,
            'post_id': None,
            'message': 'Newsletter content is empty'
        }
    
    # Convert content to Beehiiv blocks format
    blocks = convert_content_to_beehiiv_blocks(content)
    
    # Prepare API request
    url = f"https://api.beehiiv.com/v2/publications/{pub_id}/posts"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'title': subject,
        'blocks': blocks
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        
        # Beehiiv API returns post data
        post_id = result.get('id')
        published_url = result.get('url') or result.get('web_url')
        
        return {
            'success': True,
            'published_url': published_url,
            'post_id': post_id,
            'message': 'Newsletter published to Beehiiv successfully'
        }
    except requests.exceptions.HTTPError as e:
        error_msg = f"Beehiiv API error: {e.response.status_code}"
        try:
            error_data = e.response.json()
            error_msg += f" - {error_data.get('message', str(e))}"
        except:
            error_msg += f" - {str(e)}"
        
        return {
            'success': False,
            'published_url': None,
            'post_id': None,
            'message': error_msg
        }
    except Exception as e:
        return {
            'success': False,
            'published_url': None,
            'post_id': None,
            'message': f"Failed to publish to Beehiiv: {str(e)}"
        }

def publish_to_telegram(derivative, chat_id):
    """
    Publish to Telegram
    """
    content = derivative.get('content', '')
    if not content:
        raise ValueError("Derivative has no content")
    
    try:
        import requests
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found")
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        response = requests.post(url, json={
            'chat_id': chat_id,
            'text': content,
            'parse_mode': 'Markdown'
        })
        response.raise_for_status()
        result = response.json()
        
        return {
            'success': True,
            'message_id': result.get('result', {}).get('message_id'),
            'message': 'Published to Telegram'
        }
    except Exception as e:
        raise Exception(f"Failed to publish to Telegram: {str(e)}")

def publish_to_social(derivative, platform):
    """
    Publish to social media platforms
    Note: Placeholder - implement Buffer/Hypefury API
    """
    # TODO: Implement Buffer or Hypefury API integration
    content = derivative.get('content', '')
    
    return {
        'success': True,
        'published_url': None,
        'message': f'Queued for {platform} (API integration needed)'
    }

def publish_queued_derivatives():
    """
    Cron job: Check for queued derivatives and publish them
    Should be called periodically (every 5 minutes)
    """
    now = datetime.now()
    data = load_derivatives()
    
    published_count = 0
    errors = []
    
    for derivative in data['derivatives']:
        status = (derivative.get('metadata') or {}).get('status')
        scheduled_for = derivative.get('scheduled_for')
        
        if status == 'queued' and scheduled_for:
            try:
                scheduled_dt = datetime.fromisoformat(scheduled_for.replace('Z', '+00:00'))
                if scheduled_dt <= now:
                    # Time to publish
                    deriv_type = derivative.get('type')
                    post_id = derivative.get('post_id')
                    
                    # Get client info for chat_id
                    try:
                        with open('clients.json', 'r') as f:
                            clients_data = json.load(f)
                    except FileNotFoundError:
                        print(f"⚠️ clients.json not found, skipping scheduled publish")
                        clients_data = {"clients": []}
                    
                    # Find client from post
                    from .center_post import get_post
                    post = get_post(post_id)
                    if post:
                        client_id = post.get('client_id')
                        client = next((c for c in clients_data.get('clients', []) if c.get('client_id') == client_id), None)
                        chat_id = client.get('chat_id') if client else None
                        
                        # Publish based on type
                        if deriv_type == 'newsletter':
                            result = publish_to_beehiiv(derivative, client_id)
                        elif deriv_type == 'telegram' and chat_id:
                            result = publish_to_telegram(derivative, chat_id)
                        elif deriv_type.startswith('social_'):
                            platform = (derivative.get('metadata') or {}).get('platform', 'unknown')
                            result = publish_to_social(derivative, platform)
                        else:
                            result = {'success': False, 'message': 'Unknown derivative type'}
                        
                        if result.get('success'):
                            derivative['metadata']['status'] = 'published'
                            derivative['published_at'] = datetime.now().isoformat()
                            published_count += 1
                        else:
                            derivative['metadata']['status'] = 'failed'
                            errors.append(f"{deriv_type}: {result.get('message', 'Unknown error')}")
            except Exception as e:
                derivative['metadata']['status'] = 'failed'
                errors.append(f"{derivative.get('type', 'unknown')}: {str(e)}")
    
    save_derivatives(data)
    
    return {
        'published': published_count,
        'errors': errors
    }

