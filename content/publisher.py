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
                post_num = derivative.get('metadata', {}).get('post_number', 1)
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

def publish_to_beehiiv(derivative):
    """
    Publish newsletter to Beehiiv
    Note: This is a placeholder - implement actual Beehiiv API call
    """
    # TODO: Implement Beehiiv API integration
    # Use existing get_beehiiv_metrics() pattern
    content = derivative.get('content', '')
    subject = derivative.get('metadata', {}).get('subject', '')
    
    # For now, just mark as published
    return {
        'success': True,
        'published_url': None,  # Would be actual Beehiiv URL
        'message': 'Newsletter queued for Beehiiv (API integration needed)'
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
        status = derivative.get('metadata', {}).get('status')
        scheduled_for = derivative.get('scheduled_for')
        
        if status == 'queued' and scheduled_for:
            try:
                scheduled_dt = datetime.fromisoformat(scheduled_for.replace('Z', '+00:00'))
                if scheduled_dt <= now:
                    # Time to publish
                    deriv_type = derivative.get('type')
                    post_id = derivative.get('post_id')
                    
                    # Get client info for chat_id
                    with open('clients.json', 'r') as f:
                        clients_data = json.load(f)
                    
                    # Find client from post
                    from .center_post import get_post
                    post = get_post(post_id)
                    if post:
                        client_id = post.get('client_id')
                        client = next((c for c in clients_data['clients'] if c.get('client_id') == client_id), None)
                        chat_id = client.get('chat_id') if client else None
                        
                        # Publish based on type
                        if deriv_type == 'newsletter':
                            result = publish_to_beehiiv(derivative)
                        elif deriv_type == 'telegram' and chat_id:
                            result = publish_to_telegram(derivative, chat_id)
                        elif deriv_type.startswith('social_'):
                            platform = derivative.get('metadata', {}).get('platform', 'unknown')
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

