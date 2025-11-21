"""
Migration script to convert old clients.json structure to new modular structure
"""
import json
import os
from datetime import datetime
import uuid

def get_channel_emoji(channel_type):
    """Get emoji for channel type"""
    emoji_map = {
        'social': '📱',
        'content': '📝',
        'owned': '🌐',
        'paid': '💰',
        'referral': '👥',
        'event': '🎤'
    }
    return emoji_map.get(channel_type, '📊')

def migrate_client(old_client):
    """Convert old client structure to new modular structure"""
    client_id = old_client.get('client_id', f"client_{uuid.uuid4().hex[:8]}")
    
    # Detect business type from existing data
    business_type = "coach"  # Default, can be updated via onboarding
    
    # Build awareness channels from existing data
    awareness_channels = []
    
    # Blog/Vercel - add even if placeholder (user can configure later)
    vercel_project_id = old_client.get('vercel_project_id', 'your_vercel_project_id')
    blog_channel = {
        "name": "Blog",
        "type": "owned",
        "tracking": "auto" if (vercel_project_id and vercel_project_id != 'your_vercel_project_id') else "manual",
        "source": "vercel",
        "metric_name": "blog_visitors"
    }
    if blog_channel["tracking"] == "auto":
        blog_channel["api_connection"] = {
            "project_id": vercel_project_id,
            "token": "env_var"
        }
    awareness_channels.append(blog_channel)
    
    # Instagram - add even if placeholder
    instagram_id = old_client.get('instagram_id', 'your_instagram_user_id')
    ig_channel = {
        "name": "Instagram",
        "type": "social",
        "tracking": "auto" if (instagram_id and instagram_id != 'your_instagram_user_id') else "manual",
        "source": "instagram",
        "metric_name": "ig_impressions"
    }
    if ig_channel["tracking"] == "auto":
        ig_channel["api_connection"] = {
            "user_id": instagram_id,
            "access_token": old_client.get('instagram_token') or "env_var"
        }
    awareness_channels.append(ig_channel)
    
    # LinkedIn (manual, always available)
    awareness_channels.append({
        "name": "LinkedIn",
        "type": "social",
        "tracking": "manual",
        "metric_name": "linkedin_impressions"
    })
    
    # Build capture config
    beehiiv_pub_id = old_client.get('beehiiv_pub_id', 'your_beehiiv_pub_id')
    capture_config = {
        "platform": "Beehiiv",
        "platform_id": "beehiiv",
        "method": "Website popup",
        "description": "Newsletter signup",
        "location": "Website",
        "tracking": "auto",
        "api_connection": {
            "type": "beehiiv",
            "api_key": "env_var",
            "pub_id": beehiiv_pub_id if beehiiv_pub_id != 'your_beehiiv_pub_id' else "env_var"
        }
    }
    
    # Build nurture config
    nurture_config = {
        "method": "Weekly newsletter",
        "frequency": "Weekly",
        "platform": "Beehiiv",
        "content_types": ["Tips", "Updates"],
        "tracking": "auto"
    }
    
    # Build conversion touchpoints
    conversion_touchpoints = [
        {
            "name": "Discovery call",
            "type": "call",
            "tracking": "manual",
            "metric_name": "calls_booked"
        }
    ]
    
    # Build products
    products = [
        {
            "name": "Retainer",
            "price": 1000,
            "currency": "USD",
            "billing": "monthly",
            "type": "service"
        }
    ]
    
    # Build connected accounts
    connected_accounts = {
        "linkedin": {
            "connected": False,
            "tracking": "manual",
            "status": "manual_entry"
        }
    }
    
    # Instagram connection
    if old_client.get('instagram_id') and old_client['instagram_id'] != 'your_instagram_user_id':
        connected_accounts["instagram"] = {
            "connected": True,
            "user_id": old_client.get('instagram_id'),
            "access_token": "env_var",
            "status": "active"
        }
    
    # Email platform connection
    if old_client.get('beehiiv_pub_id') and old_client['beehiiv_pub_id'] != 'your_beehiiv_pub_id':
        connected_accounts["email_platform"] = {
            "type": "beehiiv",
            "connected": True,
            "api_key": "env_var",
            "status": "active"
        }
    
    # Website connection
    if old_client.get('vercel_project_id') and old_client['vercel_project_id'] != 'your_vercel_project_id':
        connected_accounts["website"] = {
            "type": "vercel",
            "connected": True,
            "project_id": old_client.get('vercel_project_id'),
            "token": "env_var",
            "status": "active"
        }
    
    # Build new client structure
    new_client = {
        "client_id": client_id,
        "name": old_client.get('name', 'Unnamed Client'),
        "chat_id": old_client.get('chat_id'),
        "created_at": old_client.get('created_at', datetime.now().strftime('%Y-%m-%d')),
        "status": old_client.get('status', 'active'),
        
        "business": {
            "type": business_type,
            "description": "",
            "target_audience": ""
        },
        
        "funnel_structure": {
            "awareness": {
                "channels": awareness_channels
            },
            "capture": capture_config,
            "nurture": nurture_config,
            "conversion": {
                "touchpoints": conversion_touchpoints,
                "tracking_method": "manual"
            },
            "products": products
        },
        
        "connected_accounts": connected_accounts,
        
        "report_settings": {
            "frequency": "weekly",
            "day": "Monday",
            "time": "09:00",
            "timezone": "Europe/Berlin",
            "language": "en"
        },
        
        "custom_benchmarks": {
            "capture_rate": {"target": 4, "min": 2, "stretch": 6},
            "open_rate": {"target": 40, "min": 35, "stretch": 50},
            "inquiry_rate": {"target": 1.5, "min": 0.5, "stretch": 2.5},
            "close_rate": {"target": 40, "min": 30, "stretch": 60}
        },
        
        "onboarding": {
            "completed": True,
            "completed_at": datetime.now().isoformat(),
            "template_used": "default"
        }
    }
    
    # Preserve old fields for backward compatibility
    if old_client.get('beehiiv_pub_id'):
        new_client['_legacy'] = {
            'beehiiv_pub_id': old_client.get('beehiiv_pub_id'),
            'instagram_id': old_client.get('instagram_id'),
            'instagram_token': old_client.get('instagram_token'),
            'vercel_project_id': old_client.get('vercel_project_id')
        }
    
    return new_client

def migrate_clients_file(backup=True):
    """Migrate clients.json to new structure"""
    if not os.path.exists('clients.json'):
        print("❌ clients.json not found")
        return False
    
    # Backup original
    if backup:
        backup_name = f"clients.json.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open('clients.json', 'r') as f:
            old_data = f.read()
        with open(backup_name, 'w') as f:
            f.write(old_data)
        print(f"✅ Backed up to {backup_name}")
    
    # Load old structure
    with open('clients.json', 'r') as f:
        old_data = json.load(f)
    
    # Migrate each client
    new_clients = []
    for old_client in old_data.get('clients', []):
        new_client = migrate_client(old_client)
        new_clients.append(new_client)
    
    # Create new structure
    new_data = {
        "clients": new_clients
    }
    
    # Write new structure
    with open('clients.json', 'w') as f:
        json.dump(new_data, f, indent=2)
    
    print(f"✅ Migrated {len(new_clients)} client(s) to new structure")
    return True

if __name__ == "__main__":
    migrate_clients_file()

