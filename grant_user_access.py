#!/usr/bin/env python3
"""
Grant access to existing user (works with OAuth users like GitHub)
This script finds an existing user by email and grants them access to all clients
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def grant_user_access():
    """Grant access to existing user (OAuth or email/password)"""
    try:
        from supabase import create_client
        from content.supabase_storage import load_clients_from_supabase
        
        supabase_url = os.getenv('SUPABASE_URL')
        # Use service_role key for admin operations
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ Supabase not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env")
            print("   Get SUPABASE_SERVICE_ROLE_KEY from Supabase Dashboard → Settings → API → service_role key")
            return False
        
        # Create admin client with service_role key
        admin_client = create_client(supabase_url, supabase_key)
    except ImportError:
        print("❌ Supabase package not installed. Run: pip install supabase")
        return False
    
    # Get user email from environment, command line arg, or prompt
    user_email = os.getenv('ADMIN_EMAIL')
    if not user_email and len(sys.argv) > 1:
        user_email = sys.argv[1]
    if not user_email:
        try:
            user_email = input("Enter user email to grant access: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Email is required")
            print("   Usage: python grant_user_access.py <email>")
            print("   Or set: export ADMIN_EMAIL=your@email.com")
            return False
    
    if not user_email:
        print("❌ Email is required")
        return False
    
    try:
        # Find existing user by email
        print(f"🔍 Looking for user: {user_email}")
        users_response = admin_client.auth.admin.list_users()
        
        existing_user = None
        # Handle different response formats
        users_list = None
        if hasattr(users_response, 'users'):
            users_list = users_response.users
        elif isinstance(users_response, list):
            users_list = users_response
        elif hasattr(users_response, 'data'):
            users_list = users_response.data
        
        if users_list:
            for user in users_list:
                # Handle both dict and object formats
                user_email_check = user.email if hasattr(user, 'email') else user.get('email')
                if user_email_check == user_email:
                    existing_user = user
                    break
        
        if not existing_user:
            print(f"❌ User with email {user_email} not found")
            print("   Please sign up first via /signup or log in with GitHub OAuth")
            return False
        
        # Handle both dict and object formats
        if isinstance(existing_user, dict):
            user_id = existing_user.get('id')
            user_email_found = existing_user.get('email')
            provider = existing_user.get('app_metadata', {}).get('provider', 'email')
        else:
            user_id = existing_user.id
            user_email_found = existing_user.email
            provider = existing_user.app_metadata.get('provider', 'email') if hasattr(existing_user, 'app_metadata') else 'email'
        
        print(f"✅ Found user: {user_id}")
        print(f"   Email: {user_email_found}")
        print(f"   Provider: {provider}")
        if provider != 'email':
            print(f"   ✅ OAuth user (no password needed)")
        
        # Get all clients
        try:
            response = admin_client.table('clients').select('client_id').execute()
            all_clients = response.data if response.data else []
        except Exception as e:
            print(f"⚠️ Error loading clients: {e}")
            all_clients = []
        
        if not all_clients:
            print("⚠️ No clients found. Create clients first or run migrate_clients_to_supabase.py")
            return True
        
        # Grant access to all clients as owner
        print(f"\n📦 Granting owner access to {len(all_clients)} client(s)...")
        
        granted = 0
        errors = 0
        
        for client_data in all_clients:
            client_id = client_data.get('client_id')
            if not client_id:
                continue
            
            try:
                # Insert into user_clients table using admin client
                admin_client.table('user_clients').upsert({
                    'user_id': user_id,
                    'client_id': client_id,
                    'role': 'owner'
                }, on_conflict='user_id,client_id').execute()
                
                print(f"   ✅ Granted owner access to: {client_id}")
                granted += 1
            except Exception as e:
                print(f"   ❌ Error granting access to {client_id}: {e}")
                errors += 1
        
        print(f"\n✅ Setup complete!")
        print(f"   User: {user_email} ({provider})")
        print(f"   Access granted: {granted} client(s) as owner")
        if errors > 0:
            print(f"   Errors: {errors}")
        
        return granted > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = grant_user_access()
    sys.exit(0 if success else 1)

