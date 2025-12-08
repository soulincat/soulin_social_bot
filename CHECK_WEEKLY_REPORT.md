# 🔍 Check Why Weekly Report Didn't Send

If it's Monday and you didn't receive a report, follow these steps:

## Step 1: Check if GitHub Actions Workflow Ran

1. Go to: https://github.com/soulincat/soulin_social_bot/actions
2. Look for "Weekly Metrics Report" workflow
3. Check if it ran today (Monday)
4. Click on the latest run to see the logs

## Step 2: Check Workflow Status

**If workflow shows:**
- ✅ **Green checkmark** = It ran successfully (check Telegram)
- ❌ **Red X** = It failed (check the error logs)
- ⏸️ **Yellow circle** = It's still running
- ⚪ **No run** = It didn't trigger (see Step 3)

## Step 3: If Workflow Didn't Run

The workflow is scheduled for **9 AM UTC every Monday**. 

**Possible reasons it didn't run:**
1. **Actions might be disabled:**
   - Go to: Settings → Actions → General
   - Make sure "Allow all actions" is enabled

2. **Schedule might not have triggered yet:**
   - Check what time it is in UTC
   - 9 AM UTC = 1 AM PST / 4 AM EST / 9 AM GMT
   - If it's before 9 AM UTC, wait a bit

3. **Workflow might have failed silently:**
   - Check the Actions tab for any failed runs

## Step 4: Manually Trigger the Workflow

You can run it manually right now:

1. Go to: https://github.com/soulincat/soulin_social_bot/actions/workflows/weekly-report.yml
2. Click **"Run workflow"** button (top right)
3. Click the green **"Run workflow"** button
4. Watch it run and check the logs

## Step 5: Check Common Issues

### Issue: "CLIENTS_JSON not found"
- Make sure `CLIENTS_JSON` secret is set in GitHub
- Go to: Settings → Secrets → Actions
- Verify it exists and has content

### Issue: "TELEGRAM_BOT_TOKEN not found"
- Make sure `TELEGRAM_BOT_TOKEN` secret is set
- Verify the token is correct

### Issue: "Error sending to Telegram"
- Check the workflow logs for specific error
- Verify your chat_id in clients.json is correct
- Make sure the bot is still active

## Step 6: Test Locally

To test if everything works locally:

```bash
python3 cron_weekly.py
```

This will send the report immediately and show any errors.

## Quick Fix: Run It Now

If you want to send the report right now:

1. **Option A: Manual GitHub Actions Run**
   - Go to Actions → Weekly Metrics Report → Run workflow

2. **Option B: Run Locally**
   ```bash
   python3 cron_weekly.py
   ```

## Time Zone Reference

The workflow runs at **9 AM UTC every Monday**:
- **PST (Pacific)**: 1:00 AM Monday
- **EST (Eastern)**: 4:00 AM Monday  
- **GMT (UK)**: 9:00 AM Monday
- **KST (Korea)**: 6:00 PM Monday

If it's Monday but before 9 AM UTC, the workflow hasn't run yet.

