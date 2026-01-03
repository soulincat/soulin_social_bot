# Quick Setup Guide

## Set Up Admin User

### Option 1: Using the script (Recommended)

```bash
# Make sure SUPABASE_SERVICE_ROLE_KEY is in your .env file
# Then run:
./setup_admin_user.sh soulincat@gmail.com
```

### Option 2: Using environment variable

```bash
export ADMIN_EMAIL=soulincat@gmail.com
export SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
python3 grant_user_access.py
```

### Option 3: Direct command

```bash
ADMIN_EMAIL=soulincat@gmail.com python3 grant_user_access.py soulincat@gmail.com
```

## Get Your Service Role Key

1. Go to Supabase Dashboard
2. Settings → API
3. Copy the **service_role** key (not the anon key!)
4. Add it to your `.env` file:
   ```
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
   ```

**Important**: The service_role key has admin privileges. Keep it secret!

## Run Development Server

This is a **Flask app** (Python), not Node.js. Use:

```bash
# Option 1: Using npm (now works!)
npm run dev

# Option 2: Direct Python
python3 app.py

# Option 3: Using the start script
npm start
```

The server will start on `http://localhost:3000`

## Troubleshooting

### "This endpoint requires a valid Bearer token"
- Make sure `SUPABASE_SERVICE_ROLE_KEY` is set in `.env`
- Use the **service_role** key, not the anon key
- Restart your terminal after adding to `.env`

### "User not found"
- Make sure you've logged in at least once (via OAuth or signup)
- Check the email matches exactly (case-sensitive)

### "No clients found"
- Run: `python3 migrate_clients_to_supabase.py`
- Or create clients manually in Supabase Dashboard

