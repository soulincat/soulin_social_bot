# OAuth User Setup Guide

## Problem
If you're using GitHub OAuth (or other OAuth providers) to log in, you can't create users with passwords. The `setup_default_user.py` script has been updated to handle this, but there's also a simpler script for existing OAuth users.

## Solution 1: Use `grant_user_access.py` (Recommended for OAuth users)

This script finds an existing user (created via OAuth or signup) and grants them access to all projects:

```bash
# Set your email
export ADMIN_EMAIL=your@email.com

# Run the script
python grant_user_access.py
```

Or run interactively:
```bash
python grant_user_access.py
# Enter your email when prompted
```

**This works with:**
- ✅ GitHub OAuth users
- ✅ Google OAuth users  
- ✅ Email/password users
- ✅ Any existing Supabase Auth user

## Solution 2: Updated `setup_default_user.py`

The `setup_default_user.py` script now:
1. First checks if user exists (OAuth or email/password)
2. If exists, uses that user (no password needed for OAuth)
3. If doesn't exist, creates new email/password user

```bash
# For existing OAuth user
export ADMIN_EMAIL=your@email.com
python setup_default_user.py
# It will find your OAuth user and grant access

# For new email/password user
export ADMIN_EMAIL=new@email.com
export ADMIN_PASSWORD=yourpassword
python setup_default_user.py
```

## Steps for OAuth Users

1. **First, log in via OAuth** (GitHub, Google, etc.)
   - Go to `/login` or `/signup`
   - Click "Sign in with GitHub" (or your OAuth provider)
   - Complete OAuth flow
   - This creates your user in Supabase Auth

2. **Then grant access to projects:**
   ```bash
   python grant_user_access.py
   ```
   Enter your email when prompted

3. **Done!** You can now access the workspace at `/workspace`

## Workspace Dashboard

The workspace dashboard (`/workspace`) is fully implemented and shows:

- **All your projects** in a card grid
- **Key metrics** for each project:
  - Growth percentage (month-over-month)
  - Total followers (sum across platforms)
  - Monthly revenue
- **Status badges**: Active/Inactive
- **Role badges**: Owner/Editor/Viewer
- **Click any card** to go to that project's dashboard

The dashboard automatically:
- Fetches metrics from `/api/dashboard/growth`, `/api/dashboard/socials`, `/api/dashboard/products`
- Caches results for 5 minutes
- Shows loading states while fetching
- Handles empty states (no projects)

## Troubleshooting

### "User not found"
- Make sure you've logged in at least once via OAuth or signup
- Check that your email matches exactly (case-sensitive)

### "No clients found"
- Run `python migrate_clients_to_supabase.py` first
- Or create clients manually in Supabase

### "Bearer token required"
- Make sure `SUPABASE_SERVICE_ROLE_KEY` is set in `.env`
- Get it from: Supabase Dashboard → Settings → API → service_role key
- This key is required for admin operations (granting access)

