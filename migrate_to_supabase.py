#!/usr/bin/env python3
"""
Migration script to move data from JSON files to Supabase
Run this once after setting up Supabase to migrate existing data
"""
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Import Supabase storage functions
from content.supabase_storage import (
    save_posts_to_supabase,
    save_derivatives_to_supabase,
    save_pillars_to_supabase
)

def migrate_posts():
    """Migrate posts from JSON to Supabase"""
    posts_file = 'content_posts.json'
    if not os.path.exists(posts_file):
        print(f"⚠️ {posts_file} not found, skipping posts migration")
        return
    
    try:
        with open(posts_file, 'r') as f:
            data = json.load(f)
            posts = data.get('posts', [])
        
        if not posts:
            print("ℹ️ No posts to migrate")
            return
        
        print(f"📦 Migrating {len(posts)} posts to Supabase...")
        if save_posts_to_supabase(posts):
            print("✅ Posts migrated successfully!")
        else:
            print("❌ Failed to migrate posts")
    except Exception as e:
        print(f"❌ Error migrating posts: {e}")
        import traceback
        traceback.print_exc()

def migrate_derivatives():
    """Migrate derivatives from JSON to Supabase"""
    derivatives_file = 'content_derivatives.json'
    if not os.path.exists(derivatives_file):
        print(f"⚠️ {derivatives_file} not found, skipping derivatives migration")
        return
    
    try:
        with open(derivatives_file, 'r') as f:
            data = json.load(f)
            derivatives = data.get('derivatives', [])
        
        if not derivatives:
            print("ℹ️ No derivatives to migrate")
            return
        
        print(f"📦 Migrating {len(derivatives)} derivatives to Supabase...")
        if save_derivatives_to_supabase(derivatives):
            print("✅ Derivatives migrated successfully!")
        else:
            print("❌ Failed to migrate derivatives")
    except Exception as e:
        print(f"❌ Error migrating derivatives: {e}")
        import traceback
        traceback.print_exc()

def migrate_pillars():
    """Migrate pillars from JSON to Supabase"""
    pillars_file = 'content_pillars.json'
    if not os.path.exists(pillars_file):
        print(f"⚠️ {pillars_file} not found, skipping pillars migration")
        return
    
    try:
        with open(pillars_file, 'r') as f:
            data = json.load(f)
            pillars = data.get('pillars', [])
        
        if not pillars:
            print("ℹ️ No pillars to migrate")
            return
        
        print(f"📦 Migrating {len(pillars)} pillars to Supabase...")
        if save_pillars_to_supabase(pillars):
            print("✅ Pillars migrated successfully!")
        else:
            print("❌ Failed to migrate pillars")
    except Exception as e:
        print(f"❌ Error migrating pillars: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all migrations"""
    print("🚀 Starting Supabase migration...")
    print("=" * 50)
    
    # Check if Supabase is configured
    if not os.getenv('SUPABASE_URL') or not os.getenv('SUPABASE_KEY'):
        print("❌ ERROR: Supabase credentials not found!")
        print("   Please set SUPABASE_URL and SUPABASE_KEY in your .env file")
        print("   Get these from: https://app.supabase.com → Your Project → Settings → API")
        return
    
    print("✅ Supabase credentials found")
    print()
    
    migrate_posts()
    print()
    migrate_derivatives()
    print()
    migrate_pillars()
    print()
    print("=" * 50)
    print("✨ Migration complete!")
    print()
    print("📝 Next steps:")
    print("   1. Verify data in Supabase dashboard")
    print("   2. Test creating a new post to ensure Supabase is working")
    print("   3. (Optional) Backup JSON files before deleting them")

if __name__ == '__main__':
    main()


