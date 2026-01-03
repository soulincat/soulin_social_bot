#!/bin/bash
# Quick script to set up admin user
# Usage: ./setup_admin_user.sh soulincat@gmail.com

EMAIL="${1:-soulincat@gmail.com}"

echo "🔧 Setting up admin user: $EMAIL"
echo ""

# Check if SUPABASE_SERVICE_ROLE_KEY is set
if [ -z "$SUPABASE_SERVICE_ROLE_KEY" ]; then
    echo "⚠️  SUPABASE_SERVICE_ROLE_KEY not found in environment"
    echo "   Please set it in your .env file or export it:"
    echo "   export SUPABASE_SERVICE_ROLE_KEY=your_service_role_key"
    echo ""
    echo "   Get it from: Supabase Dashboard → Settings → API → service_role key"
    exit 1
fi

# Run the grant access script
export ADMIN_EMAIL="$EMAIL"
python3 grant_user_access.py "$EMAIL"

