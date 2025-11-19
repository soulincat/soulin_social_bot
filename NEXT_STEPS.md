# 🚀 Next Steps - Getting Your Metrics

Your bot is working! Now let's connect it to your data sources.

## 📋 Quick Checklist

- [x] Telegram bot token ✅
- [x] Chat ID ✅
- [ ] Beehiiv API key (if using newsletter)
- [ ] Instagram access token (if using Instagram)
- [ ] Vercel token (if using Vercel analytics)
- [ ] Update `clients.json` with your IDs

## 🔑 Getting API Keys

### Option 1: Beehiiv (Newsletter Metrics)

1. Go to [Beehiiv Dashboard](https://www.beehiiv.com/)
2. Navigate to **Settings → Integrations → API**
3. Create a new API key
4. Copy the key and add to `.env`:
   ```
   BEEHIIV_API_KEY=your_key_here
   ```
5. Get your Publication ID from the URL or API response
6. Update `clients.json` with `beehiiv_pub_id`

### Option 2: Instagram (Social Media Metrics)

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app → Choose **Business** type
3. Add **Instagram Graph API** product
4. Get a long-lived access token (60 days)
5. Add to `.env`:
   ```
   INSTAGRAM_ACCESS_TOKEN=your_token_here
   INSTAGRAM_USER_ID=your_instagram_user_id
   ```
6. Update `clients.json` with `instagram_id`

**Note:** Instagram tokens expire after 60 days. You'll need to refresh them.

### Option 3: Vercel (Website Analytics)

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Navigate to **Settings → Tokens**
3. Create a new token
4. Add to `.env`:
   ```
   VERCEL_TOKEN=your_token_here
   ```
5. Get your Project ID from project settings
6. Update `clients.json` with `vercel_project_id`

## 🧪 Testing Without Full Setup

You can test the bot structure even without all API keys. The bot will show errors for missing services, but you can see the format.

**To test with mock data**, I can create a test version that uses sample data.

## 📝 Update clients.json

Edit `clients.json` and replace the placeholder values:

```json
{
  "clients": [
    {
      "name": "My Account",
      "chat_id": "8116874871",
      "beehiiv_pub_id": "pub_abc123",  // Replace this
      "instagram_id": "17841405309211844",  // Replace this
      "vercel_project_id": "prj_xyz789"  // Replace this
    }
  ]
}
```

## 🎯 Run Your First Report

Once you have at least one API key set up:

```bash
python3 bot.py
```

This will:
1. Fetch metrics from all configured services
2. Format a beautiful report
3. Send it to your Telegram

## 🔄 Automation Options

### Option A: Local Schedule (Your Computer)
```bash
python3 bot_scheduled.py
```
Runs every Monday at 9 AM. Keep your computer on.

### Option B: GitHub Actions (Free, Recommended)
1. Push your code to GitHub
2. Go to Settings → Secrets → Actions
3. Add all your API keys as secrets
4. The workflow will run automatically every Monday

### Option C: Cron Job (VPS/Server)
```bash
crontab -e
# Add: 0 9 * * 1 cd /path/to/soulin_social_bot && python3 bot.py
```

## ❓ Which Services Do You Want to Use?

Let me know which metrics you want to track:
- ✅ Newsletter (Beehiiv)
- ✅ Instagram
- ✅ Website (Vercel)
- ✅ All of the above

I can help you set up any of these!

