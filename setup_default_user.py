#!/usr/bin/env python3
"""
Setup default admin user and grant access to all clients
This is optional - run after setting up Supabase Auth
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def setup_default_user():
    """Create default admin user and grant access to all clients"""
    try:
        from supabase import create_client
        from content.supabase_storage import load_clients_from_supabase
        
        supabase_url = os.getenv('SUPABASE_URL')
        # Use service_role key for admin operations (creating users)
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ Supabase not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env")
            print("   Note: SUPABASE_SERVICE_ROLE_KEY is required for creating users.")
            print("   Get it from Supabase Dashboard → Settings → API → service_role key")
            return False
        
        # Create admin client with service_role key
        admin_client = create_client(supabase_url, supabase_key)
        
        # Also get regular client for data operations
        from content.supabase_storage import get_supabase_client
        data_client = get_supabase_client()
    except ImportError:
        print("❌ Supabase package not installed. Run: pip install supabase")
        return False
    
    # Get user email from environment or prompt
    user_email = os.getenv('ADMIN_EMAIL')
    if not user_email:
        user_email = input("Enter admin user email: ").strip()
    
    if not user_email:
        print("❌ Email is required")
        return False
    
    try:
        # First, try to find existing user by email
        print(f"🔍 Looking for existing user: {user_email}")
        try:
            # List users and find by email
            users_response = admin_client.auth.admin.list_users()
            existing_user = None
            if users_response and users_response.users:
                for user in users_response.users:
                    if user.email == user_email:
                        existing_user = user
                        break
            
            if existing_user:
                print(f"✅ Found existing user: {existing_user.id}")
                user_id = existing_user.id
                print(f"   Provider: {existing_user.app_metadata.get('provider', 'email')}")
                if existing_user.app_metadata.get('provider') != 'email':
                    print(f"   ⚠️  Note: This user uses {existing_user.app_metadata.get('provider')} OAuth (no password needed)")
            else:
                # User doesn't exist, create new one
                print(f"📝 Creating new user: {user_email}")
                
                # Get user password
                user_password = os.getenv('ADMIN_PASSWORD')
                if not user_password:
                    import getpass
                    user_password = getpass.getpass("Enter admin user password (min 6 chars): ").strip()
                
                if len(user_password) < 6:
                    print("❌ Password must be at least 6 characters")
                    return False
                
                auth_response = admin_client.auth.admin.create_user({
                    "email": user_email,
                    "password": user_password,
                    "email_confirm": True,  # Auto-confirm email
                    "user_metadata": {
                        "name": "Admin",
                        "role": "admin"
                    }
                })
                
                if not auth_response.user:
                    print("❌ Failed to create user")
                    return False
                
                user_id = auth_response.user.id
                print(f"✅ Created user: {user_id}")
        except Exception as list_error:
            # If list_users fails, try to create user directly
            print(f"⚠️  Could not list users: {list_error}")
            print(f"📝 Attempting to create user: {user_email}")
            
            user_password = os.getenv('ADMIN_PASSWORD')
            if not user_password:
                import getpass
                user_password = getpass.getpass("Enter admin user password (min 6 chars): ").strip()
            
            if len(user_password) < 6:
                print("❌ Password must be at least 6 characters")
                return False
            
            auth_response = admin_client.auth.admin.create_user({
                "email": user_email,
                "password": user_password,
                "email_confirm": True,
                "user_metadata": {
                    "name": "Admin",
                    "role": "admin"
                }
            })
            
            if not auth_response.user:
                print("❌ Failed to create user")
                return False
            
            user_id = auth_response.user.id
            print(f"✅ Created user: {user_id}")
        
        # Get all clients
        if data_client:
            all_clients = load_clients_from_supabase()
        else:
            # Try to load from Supabase directly using admin client
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
        print(f"📦 Granting access to {len(all_clients)} client(s)...")
        
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
            except Exception as e:
                print(f"   ❌ Error granting access to {client_id}: {e}")
        
        print(f"\n✅ Setup complete!")
        print(f"   User: {user_email}")
        print(f"   Access: {len(all_clients)} client(s) as owner")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up user: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = setup_default_user()
    sys.exit(0 if success else 1)

