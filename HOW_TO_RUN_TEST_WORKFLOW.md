# 🧪 How to Run the Test Secrets Configuration Workflow

## Step-by-Step Instructions

### 1. Go to Your GitHub Repository
Open: `https://github.com/soulincat/soulin_social_bot`

### 2. Click on "Actions" Tab
- Located in the top menu bar of your repository
- You should see a list of workflows

### 3. Find "Test Secrets Configuration"
- Look for the workflow named **"Test Secrets Configuration"** in the left sidebar
- Click on it

### 4. Click "Run workflow"
- You'll see a button on the right side that says **"Run workflow"**
- Click the dropdown arrow next to it
- Then click the green **"Run workflow"** button

### 5. Watch the Workflow Run
- The workflow will start running
- Click on the running workflow to see the progress
- You'll see output showing:
  - ✅ Which secrets are set
  - ❌ Which secrets are missing
  - Validation results

## What the Test Will Show

The workflow will check:

✅ **TELEGRAM_BOT_TOKEN**
- Whether it's set
- Length of the token

✅ **CLIENTS_JSON**
- Whether it's set
- Whether it's valid JSON format

⚪ **Optional Secrets** (won't fail if missing):
- BEEHIIV_API_KEY
- INSTAGRAM_ACCESS_TOKEN
- VERCEL_TOKEN

## Expected Output

If secrets are set correctly, you'll see:
```
✅ TELEGRAM_BOT_TOKEN is set (length: XX chars)
✅ CLIENTS_JSON is set (length: XXX chars)
✅ CLIENTS_JSON is valid JSON
✅ All required secrets are configured!
```

If secrets are missing, you'll see:
```
❌ TELEGRAM_BOT_TOKEN is NOT set
❌ CLIENTS_JSON is NOT set
❌ Missing required secrets. Please add them in Settings → Secrets
```

## Troubleshooting

**Can't find the workflow?**
- Make sure you're on the `main` branch
- Check that `.github/workflows/test-secrets.yml` exists
- Refresh the Actions page

**Workflow not showing up?**
- It might take a few seconds to appear after pushing
- Try refreshing the page
- Make sure Actions are enabled: Settings → Actions → General

**Workflow fails?**
- Check the workflow logs for specific error messages
- Verify secrets are added in: Settings → Secrets and variables → Actions
- Make sure secret names match exactly (case-sensitive)

## Quick Links

- **Repository Actions**: https://github.com/soulincat/soulin_social_bot/actions
- **Secrets Settings**: https://github.com/soulincat/soulin_social_bot/settings/secrets/actions
- **Test Workflow**: https://github.com/soulincat/soulin_social_bot/actions/workflows/test-secrets.yml

## Next Steps After Test Passes

Once the test passes:
1. ✅ Your secrets are configured correctly
2. ✅ You can run the "Weekly Metrics Report" workflow
3. ✅ Reports will be sent automatically every Monday at 9 AM UTC

