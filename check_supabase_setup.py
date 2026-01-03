#!/usr/bin/env python3
"""
Check if Supabase is properly configured
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 Checking Supabase Configuration...\n")

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_ANON_KEY')
service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

checks = {
    'SUPABASE_URL': supabase_url,
    'SUPABASE_KEY (anon)': supabase_key,
    'SUPABASE_SERVICE_ROLE_KEY': service_role_key
}

all_good = True
for key, value in checks.items():
    if value:
        print(f"✅ {key}: Set ({value[:20]}...)")
    else:
        print(f"❌ {key}: Not set")
        all_good = False

print()

if not all_good:
    print("⚠️  Missing configuration!")
    print("\nTo set up admin user, you need:")
    print("1. SUPABASE_URL - Your Supabase project URL")
    print("2. SUPABASE_SERVICE_ROLE_KEY - Get from Supabase Dashboard → Settings → API")
    print("\nAdd these to your .env file")
else:
    print("✅ All Supabase keys are configured!")
    if service_role_key:
        print("\nYou can now run:")
        print("  python3 grant_user_access.py soulincat@gmail.com")
    else:
        print("\n⚠️  SUPABASE_SERVICE_ROLE_KEY is needed for admin operations")

