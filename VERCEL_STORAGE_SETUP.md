# Vercel Storage Setup Guide

## Problem

Vercel serverless functions have a **read-only filesystem**, so JSON files cannot be written. This means content created on Vercel won't persist between deployments.

## Solution: Use Vercel KV (Redis)

Vercel KV is a serverless Redis database that works seamlessly with Vercel deployments.

## Setup Steps

### 1. Create Vercel KV Database

1. Go to your Vercel project dashboard
2. Navigate to **Storage** → **Create Database**
3. Select **KV** (Key-Value store)
4. Choose a name (e.g., `soulin-kv`)
5. Select a region close to your users
6. Click **Create**

### 2. Get Connection Details

After creating the KV database:

1. Go to **Settings** → **Environment Variables**
2. Vercel automatically adds:
   - `KV_REST_API_URL` - The REST API endpoint
   - `KV_REST_API_TOKEN` - Authentication token

These are automatically available in your serverless functions.

### 3. Verify Setup

The code will automatically detect and use Vercel KV if:
- `KV_REST_API_URL` environment variable is set
- `KV_REST_API_TOKEN` environment variable is set

You should see this in your logs:
```
✅ Connected to Vercel KV
✅ Saved posts to Vercel KV
```

## How It Works

The storage system tries three methods in order:

1. **Vercel KV** (if configured) - Persistent, works across deployments
2. **Local JSON files** (if filesystem is writable) - For local development
3. **In-memory cache** (fallback) - Only for current session

## Alternative: Use a Database

If you prefer a full database, consider:

- **Vercel Postgres** - SQL database
- **Supabase** - PostgreSQL with additional features
- **MongoDB Atlas** - NoSQL database
- **PlanetScale** - MySQL-compatible

For these, you'll need to update the storage layer in `content/storage.py`.

## Testing Locally

For local development, the system will use JSON files. To test with KV:

1. Create a `.env.local` file
2. Add your KV credentials:
   ```
   KV_REST_API_URL=https://your-kv.upstash.io
   KV_REST_API_TOKEN=your-token-here
   ```
3. Run your Flask app: `python app.py`

## Troubleshooting

**"KV not available" message:**
- Check that `KV_REST_API_URL` and `KV_REST_API_TOKEN` are set in Vercel
- Verify the KV database is created and active
- Check Vercel logs for connection errors

**Data still not persisting:**
- Ensure KV is properly configured (see logs for "✅ Connected to Vercel KV")
- Check that the storage functions are being called
- Verify environment variables are set in Vercel dashboard

