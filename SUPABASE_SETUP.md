# Supabase Setup Guide

This guide will help you set up Supabase for persistent data storage in your content system.

## Why Supabase?

- ✅ **Relationships**: Proper foreign keys between posts, derivatives, pillars
- ✅ **SQL Queries**: Complex filtering, aggregations, analytics
- ✅ **Free Tier**: 500MB database, 2GB bandwidth
- ✅ **Better for Growth**: Scales with your needs

## Step 1: Create Supabase Project

1. Go to [https://app.supabase.com](https://app.supabase.com)
2. Sign up or log in
3. Click "New Project"
4. Fill in:
   - **Name**: `soulin-social-bot` (or your choice)
   - **Database Password**: (save this securely)
   - **Region**: Choose closest to you
5. Click "Create new project"
6. Wait 2-3 minutes for setup to complete

## Step 2: Get API Credentials

1. In your Supabase project, go to **Settings** → **API**
2. Copy these values:
   - **Project URL** → This is your `SUPABASE_URL`
   - **anon public** key → This is your `SUPABASE_KEY` (or `SUPABASE_ANON_KEY`)

## Step 3: Run Database Schema

1. In Supabase, go to **SQL Editor**
2. Click "New query"
3. Open `supabase_schema.sql` from this project
4. Copy and paste the entire SQL into the editor
5. Click "Run" (or press Cmd/Ctrl + Enter)
6. You should see "Success. No rows returned"

This creates:
- `clients` table (stores projects/clients)
- `user_clients` table (user access control)
- `user_settings` table (user preferences)
- `api_credentials` table (Beehiiv and other API credentials)
- `posts` table
- `derivatives` table
- `pillars` table
- `content_metrics` table
- Indexes for performance
- Auto-update triggers

## Step 4: Configure Environment Variables

Add to your `.env` file:

```bash
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
```

Or for Vercel, add these as environment variables:
- Go to Vercel Dashboard → Your Project → Settings → Environment Variables
- Add `SUPABASE_URL` and `SUPABASE_KEY`

## Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs the `supabase` Python client.

## Step 6: Enable Supabase Auth

1. In Supabase Dashboard, go to **Authentication** → **Providers**
2. Enable **Email** provider (enabled by default)
3. Optionally enable **Google**, **GitHub** for OAuth login
4. Configure email templates if needed

## Step 7: Migrate Existing Data (Optional)

If you have existing JSON files with data:

```bash
# Migrate content data
python migrate_to_supabase.py

# Migrate clients data
python migrate_clients_to_supabase.py
```

This will migrate:
- `content_posts.json` → `posts` table
- `content_derivatives.json` → `derivatives` table
- `content_pillars.json` → `pillars` table
- `clients.json` → `clients` table

## Step 8: Create Default Admin User (Optional)

After migrating clients, create an admin user with access to all projects:

```bash
python setup_default_user.py
```

Or set environment variables:
```bash
export ADMIN_EMAIL=your@email.com
export ADMIN_PASSWORD=yourpassword
python setup_default_user.py
```

## Step 9: Test It

1. Start your Flask server: `python app.py`
2. Create a new post via the web interface
3. Check Supabase dashboard → **Table Editor** → `posts` table
4. You should see your new post!

## How It Works

The system uses a **fallback chain**:

1. **Supabase** (primary) - Recommended for production
2. **Vercel KV** (fallback) - If Supabase not configured
3. **JSON files** (fallback) - For local development
4. **In-memory cache** (always) - For current session

This means:
- ✅ Works immediately even without Supabase (uses JSON files locally)
- ✅ Automatically uses Supabase when configured
- ✅ No code changes needed - just set environment variables

## Troubleshooting

### "Supabase credentials not found"
- Check that `SUPABASE_URL` and `SUPABASE_KEY` are in your `.env` file
- For Vercel, ensure they're set in environment variables

### "Error connecting to Supabase"
- Verify your `SUPABASE_URL` is correct (should end with `.supabase.co`)
- Verify your `SUPABASE_KEY` is the `anon public` key (not the `service_role` key)

### "Table does not exist"
- Make sure you ran `supabase_schema.sql` in the SQL Editor
- Check that tables appear in **Table Editor** in Supabase dashboard

### "Permission denied"
- Make sure you're using the `anon public` key (not `service_role`)
- Check Row Level Security (RLS) policies in Supabase if you enabled them

## Database Structure

### Posts Table
- `id` (TEXT, PRIMARY KEY)
- `client_id` (TEXT)
- `status` (TEXT) - idea, drafted, branched, approved, queued, published
- `raw_idea` (TEXT)
- `center_post` (JSONB) - Full article content
- `created_at`, `updated_at` (TIMESTAMPTZ)

### Derivatives Table
- `id` (TEXT, PRIMARY KEY)
- `post_id` (TEXT, FOREIGN KEY → posts.id)
- `type` (TEXT) - newsletter, social_x, social_linkedin, etc.
- `content` (TEXT)
- `metadata` (JSONB) - status, word_count, etc.
- `scheduled_for`, `published_at` (TIMESTAMPTZ)

### Pillars Table
- `id` (TEXT, PRIMARY KEY)
- `client_id` (TEXT)
- `name` (TEXT)
- `color` (TEXT)
- `channels` (JSONB)

### Content Metrics Table
- `id` (TEXT, PRIMARY KEY)
- `post_id` (TEXT, FOREIGN KEY → posts.id)
- `pillar_id` (TEXT, FOREIGN KEY → pillars.id)
- `metric_type` (TEXT)
- `metric_value` (NUMERIC)
- `recorded_at` (TIMESTAMPTZ)

### Clients Table
- `id` (TEXT, PRIMARY KEY) - UUID
- `client_id` (TEXT, UNIQUE) - Your client identifier
- `name` (TEXT) - Client/project name
- `status` (TEXT) - active, inactive, archived
- `brand` (JSONB) - Brand settings, socials, products
- `funnel_structure` (JSONB) - Funnel configuration
- `connected_accounts` (JSONB) - Connected social accounts
- `metadata` (JSONB) - Additional client data
- `created_at`, `updated_at` (TIMESTAMPTZ)

### User-Clients Table
- `id` (TEXT, PRIMARY KEY) - UUID
- `user_id` (TEXT) - Supabase Auth user ID
- `client_id` (TEXT, FOREIGN KEY → clients.client_id)
- `role` (TEXT) - owner, editor, viewer
- `created_at` (TIMESTAMPTZ)

### User Settings Table
- `id` (TEXT, PRIMARY KEY) - UUID
- `user_id` (TEXT, UNIQUE) - Supabase Auth user ID
- `preferences` (JSONB) - User preferences
- `created_at`, `updated_at` (TIMESTAMPTZ)

### API Credentials Table
- `id` (TEXT, PRIMARY KEY) - UUID
- `client_id` (TEXT) - References clients.client_id
- `platform` (TEXT) - beehiiv, buffer, etc.
- `pub_id` (TEXT) - Publication/platform ID
- `api_key` (TEXT) - API key (or "env_var" if stored in environment)
- `metadata` (JSONB) - Additional credential data
- `created_at`, `updated_at` (TIMESTAMPTZ)

## Next Steps

- ✅ Data is now persistent across serverless function invocations
- ✅ You can query data with SQL in Supabase dashboard
- ✅ Relationships are enforced (can't delete a post with derivatives)
- ✅ Ready for analytics and reporting features
- ✅ Multi-project workspace dashboard support
- ✅ User authentication and access control
- ✅ Beehiiv API credentials stored securely

## Security Note

The `anon public` key is safe to use in client-side code. Supabase uses Row Level Security (RLS) to protect your data. For now, we're not using RLS, but you can enable it later if needed.

For API credentials, consider using Supabase Vault for sensitive keys instead of storing them directly in the `api_credentials` table.

## Authentication

The system uses Supabase Auth for user authentication:
- Users can sign up and log in via `/login` and `/signup` pages
- Access to projects is controlled via the `user_clients` table
- Roles: `owner` (full access), `editor` (can edit), `viewer` (read-only)
- Workspace dashboard (`/workspace`) shows only projects the user has access to

## Workspace Dashboard Features

### Multi-Project Overview
The `/workspace` page displays all projects accessible to the current user with:
- **Growth metrics**: Month-over-month percentage change
- **Total followers**: Sum across all social platforms
- **Monthly revenue**: Aggregated from products
- **Status badges**: Active/Inactive indicators
- **Role badges**: Owner/Editor/Viewer permissions

### Performance Optimizations
The workspace API (`/api/workspace/projects`) includes:
- ✅ **Parallel Requests**: Metrics fetched concurrently using `ThreadPoolExecutor`
- ✅ **Caching**: 5-minute in-memory cache per user (reduces API calls)
- ✅ **Error Handling**: Graceful degradation if individual metrics fail
- ✅ **Cache Invalidation**: `POST /api/workspace/cache/clear` endpoint for manual cache refresh

### How Workspace Access Works
1. User logs in via Supabase Auth
2. System queries `user_clients` table for accessible `client_id`s
3. For each client, fetches metrics from:
   - `/api/dashboard/growth` (earnings, followers)
   - `/api/dashboard/socials` (social profiles)
   - `/api/dashboard/products` (revenue)
4. Results are cached for 5 minutes to improve performance
5. User clicks project card → navigates to `/dashboard?client_id=xxx`

### Setting Up User Access
After creating a user and clients, grant access:

```sql
-- Grant user access to a client
INSERT INTO user_clients (user_id, client_id, role)
VALUES (
  'user-uuid-from-auth',  -- Get from Supabase Auth dashboard
  'your-client-id',       -- From clients table
  'owner'                 -- or 'editor' or 'viewer'
);
```

Or use the `setup_default_user.py` script to create an admin user with access to all clients.


