# 🔧 Fix Missing Secrets Error

The workflow failed because required secrets are not set. Here's how to fix it:

## ❌ Error: Exit Code 1

This means one or both required secrets are missing:
- `TELEGRAM_BOT_TOKEN`
- `CLIENTS_JSON`

## ✅ How to Add Secrets

### Step 1: Go to Secrets Settings
**Direct link:** https://github.com/soulincat/soulin_social_bot/settings/secrets/actions

Or navigate:
1. Go to your repository
2. Click **Settings** (top menu)
3. Click **Secrets and variables** → **Actions** (left sidebar)

### Step 2: Add TELEGRAM_BOT_TOKEN

1. Click **"New repository secret"** button
2. **Name:** `TELEGRAM_BOT_TOKEN` (exactly like this, case-sensitive)
3. **Secret:** Paste your Telegram bot token
   - Get it from: Telegram → @BotFather → /mybots → Select your bot → API Token
   - Or from your local `.env` file: `TELEGRAM_BOT_TOKEN=...`
4. Click **"Add secret"**

### Step 3: Add CLIENTS_JSON

1. Click **"New repository secret"** button again
2. **Name:** `CLIENTS_JSON` (exactly like this, case-sensitive)
3. **Secret:** Paste your entire `clients.json` file content
   - Open your local `clients.json` file
   - Copy the ENTIRE file (all JSON content)
   - Paste it here
4. Click **"Add secret"**

## 🧪 Quick Test: Get Your Values

Run this locally to get the exact values to paste:

```bash
python3 test_secrets_local.py
```

This will show you:
- Your Telegram bot token (from .env)
- Your clients.json content (ready to copy-paste)

## ✅ Verify Secrets Are Added

After adding secrets, you should see them listed in:
**Settings → Secrets and variables → Actions**

You'll see:
- ✅ `TELEGRAM_BOT_TOKEN` (value is hidden)
- ✅ `CLIENTS_JSON` (value is hidden)

## 🔄 Run the Test Again

Once secrets are added:

1. Go back to: https://github.com/soulincat/soulin_social_bot/actions/workflows/test-secrets.yml
2. Click **"Run workflow"** again
3. This time it should pass! ✅

## 📋 Checklist

- [ ] Added `TELEGRAM_BOT_TOKEN` secret
- [ ] Added `CLIENTS_JSON` secret (entire JSON content)
- [ ] Verified both secrets appear in the list
- [ ] Re-ran the test workflow
- [ ] Workflow now passes ✅

## 🐛 Common Mistakes

**Secret name wrong:**
- ❌ `telegram_bot_token` (wrong case)
- ❌ `TELEGRAM_BOT_TOKEN ` (extra space)
- ✅ `TELEGRAM_BOT_TOKEN` (correct)

**CLIENTS_JSON not valid JSON:**
- Make sure you copy the ENTIRE file
- No extra characters before/after
- Valid JSON format (use jsonlint.com to validate)

**Token from wrong place:**
- Make sure it's from your `.env` file or @BotFather
- Should look like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

## 💡 Quick Copy-Paste Helper

If you have your `.env` file and `clients.json` locally:

1. **For TELEGRAM_BOT_TOKEN:**
   ```bash
   grep TELEGRAM_BOT_TOKEN .env
   ```
   Copy the value after the `=`

2. **For CLIENTS_JSON:**
   ```bash
   cat clients.json
   ```
   Copy the entire output

