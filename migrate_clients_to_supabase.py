#!/usr/bin/env python3
"""
Migrate clients from clients.json to Supabase
"""
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def migrate_clients_to_supabase():
    """Migrate clients from clients.json to Supabase"""
    try:
        from content.supabase_storage import get_supabase_client, save_client_to_supabase
        client = get_supabase_client()
        if not client:
            print("❌ Supabase not configured. Set SUPABASE_URL and SUPABASE_KEY in .env")
            return False
    except ImportError:
        print("❌ Supabase package not installed. Run: pip install supabase")
        return False
    
    # Load clients.json
    if not os.path.exists('clients.json'):
        print("❌ clients.json not found")
        return False
    
    try:
        with open('clients.json', 'r') as f:
            clients_data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading clients.json: {e}")
        return False
    
    clients = clients_data.get('clients', [])
    if not clients:
        print("⚠️ No clients found in clients.json")
        return False
    
    print(f"📦 Found {len(clients)} client(s) to migrate")
    
    migrated = 0
    errors = 0
    
    for client_data in clients:
        client_id = client_data.get('client_id')
        if not client_id:
            print(f"⚠️ Skipping client without client_id")
            continue
        
        try:
            # Prepare client data for Supabase
            supabase_client = {
                'client_id': client_id,
                'name': client_data.get('name', 'Unnamed Client'),
                'status': client_data.get('status', 'active'),
                'brand': client_data.get('brand', {}),
                'funnel_structure': client_data.get('funnel_structure', {}),
                'connected_accounts': client_data.get('connected_accounts', {}),
                'metadata': client_data.get('metadata', {})
            }
            
            # Save to Supabase
            if save_client_to_supabase(supabase_client):
                print(f"✅ Migrated client: {client_id} ({supabase_client['name']})")
                migrated += 1
            else:
                print(f"❌ Failed to migrate client: {client_id}")
                errors += 1
        except Exception as e:
            print(f"❌ Error migrating client {client_id}: {e}")
            errors += 1
    
    print(f"\n📊 Migration complete:")
    print(f"   ✅ Migrated: {migrated}")
    print(f"   ❌ Errors: {errors}")
    
    return migrated > 0

if __name__ == '__main__':
    success = migrate_clients_to_supabase()
    sys.exit(0 if success else 1)


