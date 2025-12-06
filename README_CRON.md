# 📅 Setting Up Weekly Cron Reports

This guide shows you how to set up automatic weekly Telegram reports using cron.

## Option 1: GitHub Actions (Recommended - Free, No Server Needed)

The `.github/workflows/weekly-report.yml` file is already configured to run every Monday at 9 AM UTC.

### Setup Steps:

1. **Add Secrets to GitHub:**
   - Go to your GitHub repo → Settings → Secrets and variables → Actions
   - Add these secrets:
     - `TELEGRAM_BOT_TOKEN` - Your Telegram bot token
     - `BEEHIIV_API_KEY` - Your Beehiiv API key (optional)
     - `INSTAGRAM_ACCESS_TOKEN` - Your Instagram token (optional)
     - `VERCEL_TOKEN` - Your Vercel token (optional)
     - `CLIENTS_JSON` - Your clients.json content (copy entire JSON)

2. **Test the Workflow:**
   - Go to Actions tab in GitHub
   - Click "Weekly Metrics Report"
   - Click "Run workflow" to test manually

3. **Verify it's scheduled:**
   - The workflow will run automatically every Monday at 9 AM UTC
   - Check the Actions tab to see run history

## Option 2: Local Cron Job (If you have a server/VPS)

### On Linux/Mac:

1. **Make the script executable:**
   ```bash
   chmod +x cron_weekly.py
   ```

2. **Edit crontab:**
   ```bash
   crontab -e
   ```

3. **Add this line (runs every Monday at 9 AM):**
   ```cron
   0 9 * * 1 cd /path/to/soulin_social_bot && /usr/bin/python3 cron_weekly.py >> /tmp/cron_weekly.log 2>&1
   ```

4. **Or run every Monday at 10 AM local time:**
   ```cron
   0 10 * * 1 cd /path/to/soulin_social_bot && /usr/bin/python3 cron_weekly.py >> /tmp/cron_weekly.log 2>&1
   ```

### On Windows (Task Scheduler):

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Weekly, Monday, 9:00 AM
4. Action: Start a program
5. Program: `python`
6. Arguments: `C:\path\to\soulin_social_bot\cron_weekly.py`
7. Start in: `C:\path\to\soulin_social_bot`

## Option 3: Run Continuously with Python Scheduler

If you have a server that's always on:

```bash
python bot_scheduled.py
```

This will run continuously and send reports every Monday at 10 AM.

## Testing

To test if everything works:

```bash
python cron_weekly.py
```

This will send reports immediately to all active clients.

## Troubleshooting

**Reports not sending?**
- Check that `TELEGRAM_BOT_TOKEN` is set in `.env`
- Verify `clients.json` exists and has valid chat IDs
- Check that clients have `"status": "active"` in clients.json
- Run `python cron_weekly.py` manually to see errors

**GitHub Actions not running?**
- Check Actions tab for errors
- Verify all secrets are set correctly
- Make sure the workflow file is in `.github/workflows/`
- Check that the cron schedule is correct (UTC time)

**Cron not working?**
- Check cron logs: `grep CRON /var/log/syslog` (Linux) or check mail
- Verify the path to Python is correct: `which python3`
- Make sure the script has execute permissions
- Test manually first: `python3 cron_weekly.py`

