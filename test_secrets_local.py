"""
Local script to test if your configuration is ready for GitHub Actions
Run this before setting up GitHub Secrets to verify everything works
"""
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_telegram_token():
    """Test if Telegram bot token is set and valid"""
    print("🔍 Testing TELEGRAM_BOT_TOKEN...")
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not found in .env file")
        print("   Add it to .env: TELEGRAM_BOT_TOKEN=your_token_here")
        return False
    
    if token == 'your_telegram_bot_token' or 'your_' in token.lower():
        print("❌ TELEGRAM_BOT_TOKEN appears to be a placeholder")
        print("   Please replace with your actual bot token from @BotFather")
        return False
    
    # Test if token format is valid (should be numbers:letters)
    if ':' not in token:
        print("⚠️ TELEGRAM_BOT_TOKEN format looks invalid (should be numbers:letters)")
        return False
    
    print(f"✅ TELEGRAM_BOT_TOKEN is set (length: {len(token)} chars)")
    
    # Try to validate token with Telegram API
    try:
        import requests
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                print(f"✅ Bot token is valid! Bot name: @{bot_info.get('username', 'unknown')}")
                return True
            else:
                print(f"❌ Bot token is invalid: {data.get('description', 'Unknown error')}")
                return False
        else:
            print(f"⚠️ Could not verify token (HTTP {response.status_code})")
            print("   Token format looks correct, but couldn't verify with Telegram API")
            return True  # Still return True if format is correct
    except Exception as e:
        print(f"⚠️ Could not verify token with API: {e}")
        print("   Token format looks correct though")
        return True
    
def test_clients_json():
    """Test if clients.json exists and is valid"""
    print("\n🔍 Testing CLIENTS_JSON...")
    
    if not os.path.exists('clients.json'):
        print("❌ clients.json file not found")
        print("   Create it from clients.json.example")
        return False
    
    try:
        with open('clients.json', 'r') as f:
            data = json.load(f)
        
        if 'clients' not in data:
            print("❌ clients.json missing 'clients' key")
            return False
        
        clients = data.get('clients', [])
        if not clients:
            print("❌ clients.json has no clients")
            return False
        
        print(f"✅ clients.json is valid JSON")
        print(f"✅ Found {len(clients)} client(s)")
        
        # Check each client
        for i, client in enumerate(clients, 1):
            name = client.get('name', 'Unknown')
            chat_id = client.get('chat_id')
            status = client.get('status', 'unknown')
            
            print(f"\n   Client {i}: {name}")
            if not chat_id:
                print(f"   ⚠️ Missing chat_id")
            else:
                print(f"   ✅ chat_id: {chat_id}")
            
            if status != 'active':
                print(f"   ⚠️ Status is '{status}' (should be 'active' for reports)")
            else:
                print(f"   ✅ Status: active")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ clients.json is not valid JSON: {e}")
        print("   Fix the JSON syntax errors")
        return False
    except Exception as e:
        print(f"❌ Error reading clients.json: {e}")
        return False

def test_optional_secrets():
    """Test optional API keys"""
    print("\n🔍 Testing optional API keys...")
    
    optional_secrets = {
        'BEEHIIV_API_KEY': 'Beehiiv newsletter metrics',
        'INSTAGRAM_ACCESS_TOKEN': 'Instagram metrics',
        'VERCEL_TOKEN': 'Vercel website analytics'
    }
    
    all_optional = True
    for key, description in optional_secrets.items():
        value = os.getenv(key)
        if not value or 'your_' in value.lower():
            print(f"⚪ {key} not set ({description}) - optional")
            all_optional = False
        else:
            print(f"✅ {key} is set ({description})")
    
    return True  # Optional secrets don't block the setup

def generate_clients_json_for_github():
    """Generate the CLIENTS_JSON value for GitHub Secrets"""
    print("\n📋 Generating CLIENTS_JSON for GitHub Secrets...")
    
    if not os.path.exists('clients.json'):
        print("❌ clients.json not found")
        return
    
    try:
        with open('clients.json', 'r') as f:
            content = f.read()
        
        # Validate it's valid JSON
        json.loads(content)
        
        print("✅ Your clients.json content (copy this to GitHub Secret 'CLIENTS_JSON'):")
        print("=" * 70)
        print(content)
        print("=" * 70)
        print("\n💡 Copy the content above and paste it as the value for CLIENTS_JSON secret in GitHub")
        
    except Exception as e:
        print(f"❌ Error reading clients.json: {e}")

def main():
    """Run all tests"""
    print("🧪 Testing Configuration for GitHub Actions")
    print("=" * 70)
    
    telegram_ok = test_telegram_token()
    clients_ok = test_clients_json()
    optional_ok = test_optional_secrets()
    
    print("\n" + "=" * 70)
    print("📊 Test Summary:")
    print("=" * 70)
    
    if telegram_ok and clients_ok:
        print("✅ All required configuration is ready!")
        print("\n📝 Next steps:")
        print("1. Go to GitHub: Settings → Secrets and variables → Actions")
        print("2. Add TELEGRAM_BOT_TOKEN secret with your bot token")
        print("3. Add CLIENTS_JSON secret with your clients.json content")
        print("\n💡 Run this script with --show-json to see what to paste for CLIENTS_JSON")
        generate_clients_json_for_github()
        return 0
    else:
        print("❌ Some required configuration is missing")
        if not telegram_ok:
            print("   - Fix TELEGRAM_BOT_TOKEN in .env file")
        if not clients_ok:
            print("   - Fix clients.json file")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())

