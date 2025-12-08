"""
Scheduler for publishing queued content derivatives
Run this periodically (every 5 minutes) to publish scheduled content
"""
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from content.publisher import publish_queued_derivatives

load_dotenv()

def main():
    """Run the content publisher scheduler"""
    print(f"📅 Content Publisher Scheduler started at {datetime.now()}")
    print("Checking for queued derivatives to publish...")
    
    try:
        result = publish_queued_derivatives()
        published = result.get('published', 0)
        errors = result.get('errors', [])
        
        if published > 0:
            print(f"✅ Published {published} derivative(s)")
        
        if errors:
            print(f"⚠️ {len(errors)} error(s):")
            for error in errors:
                print(f"   - {error}")
        
        if published == 0 and not errors:
            print("ℹ️ No derivatives ready to publish")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

