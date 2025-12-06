# 🔐 Setting Up GitHub Actions Secrets

This guide will help you set up the required secrets for the weekly report bot to work.

## 📍 Where to Find Secrets

1. Go to your GitHub repository: `https://github.com/soulincat/soulin_social_bot`
2. Click **Settings** (top menu)
3. Click **Secrets and variables** → **Actions** (left sidebar)
4. Click **New repository secret** to add each secret

## ✅ Required Secrets

### 1. `TELEGRAM_BOT_TOKEN` (Required)

**What it is:** Your Telegram bot token from BotFather

**How to get it:**
1. Open Telegram
2. Search for `@BotFather`
3. Send `/mybots`
4. Select your bot
5. Click "API Token"
6. Copy the token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

**Add to GitHub:**
- Name: `TELEGRAM_BOT_TOKEN`
- Value: Your bot token (paste it exactly as shown)

### 2. `CLIENTS_JSON` (Required)

**What it is:** Your entire `clients.json` file content

**How to get it:**
1. Open your `clients.json` file locally
2. Copy the ENTIRE file content (all JSON)
3. Make sure it's valid JSON format

**Add to GitHub:**
- Name: `CLIENTS_JSON`
- Value: Paste the entire JSON content (make sure it's valid JSON)

**Example format:**
```json
{
  "clients": [
    {
      "name": "My Account",
      "chat_id": "8116874871",
      "status": "active",
      ...
    }
  ]
}
```

## 🔧 Optional Secrets (for API integrations)

### 3. `BEEHIIV_API_KEY` (Optional)

Only needed if you're tracking newsletter metrics from Beehiiv.

**How to get it:**
1. Go to Beehiiv Dashboard
2. Settings → Integrations → API
3. Create new API key
4. Copy the key

**Add to GitHub:**
- Name: `BEEHIIV_API_KEY`
- Value: Your API key

### 4. `INSTAGRAM_ACCESS_TOKEN` (Optional)

Only needed if you're tracking Instagram metrics.

**How to get it:**
1. Go to developers.facebook.com
2. Create app → Instagram Graph API
3. Get long-lived access token
4. Copy the token

**Add to GitHub:**
- Name: `INSTAGRAM_ACCESS_TOKEN`
- Value: Your access token

### 5. `VERCEL_TOKEN` (Optional)

Only needed if you're tracking website analytics from Vercel.

**How to get it:**
1. Go to Vercel Dashboard
2. Settings → Tokens
3. Create new token
4. Copy the token

**Add to GitHub:**
- Name: `VERCEL_TOKEN`
- Value: Your Vercel token

## ✅ How to Verify Secrets Are Set

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. You should see a list of secrets (values are hidden for security)
3. Make sure you see at minimum:
   - ✅ `TELEGRAM_BOT_TOKEN`
   - ✅ `CLIENTS_JSON`

## 🧪 Test the Setup

1. Go to **Actions** tab in your GitHub repo
2. Click **Weekly Metrics Report** workflow
3. Click **Run workflow** button (top right)
4. Click the green **Run workflow** button
5. Watch the workflow run - it should complete successfully

## 🐛 Troubleshooting

**"Secret not found" error:**
- Make sure the secret name matches exactly (case-sensitive)
- Check that you're in the right repository
- Verify the secret exists in Settings → Secrets

**"Invalid JSON" error:**
- Check that `CLIENTS_JSON` is valid JSON
- Use a JSON validator: https://jsonlint.com/
- Make sure there are no extra commas or syntax errors

**"Telegram bot token invalid" error:**
- Verify the token is correct (no extra spaces)
- Make sure the bot is still active in Telegram
- Test the token manually: `curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe`

**Workflow not running:**
- Check that Actions are enabled: Settings → Actions → General
- Make sure the workflow file exists: `.github/workflows/weekly-report.yml`
- Check the cron schedule (runs every Monday at 9 AM UTC)

## 📝 Quick Checklist

- [ ] `TELEGRAM_BOT_TOKEN` added to GitHub Secrets
- [ ] `CLIENTS_JSON` added to GitHub Secrets (valid JSON)
- [ ] (Optional) `BEEHIIV_API_KEY` added if using Beehiiv
- [ ] (Optional) `INSTAGRAM_ACCESS_TOKEN` added if using Instagram
- [ ] (Optional) `VERCEL_TOKEN` added if using Vercel
- [ ] Tested workflow manually via "Run workflow"
- [ ] Workflow completed successfully

## 🎯 Next Steps

Once secrets are set:
1. The workflow will run automatically every Monday at 9 AM UTC
2. You can manually trigger it anytime via "Run workflow"
3. Check the Actions tab to see run history and logs

