# 🎯 New Features Added

## 1. ✅ On-Demand Reports (`/metrics` command)

You can now request a report anytime by sending `/metrics` to your bot!

**How to use:**
1. Run the interactive bot:
   ```bash
   python3 bot_interactive.py
   ```
2. Open Telegram and find your bot
3. Send `/metrics` to get an instant report

**Commands available:**
- `/start` - Show help message
- `/metrics` - Get your weekly metrics report on-demand

## 2. ✅ Error Alerts

The bot now sends error alerts directly to Telegram if any API fails:

- **Beehiiv API errors** → You'll get notified
- **Instagram API errors** → You'll get notified  
- **Vercel API errors** → You'll get notified

Errors appear at the bottom of your report:
```
⚠️ **API Errors:**
• ⚠️ Beehiiv API error: [error details]
• ⚠️ Instagram API error: [error details]
```

## 3. ✅ Week-over-Week Comparison

The bot now shows percentage changes compared to last week's metrics!

**Example output:**
```
📧 Newsletter
• Subscribers: 1,234 (+12% ↗️)
• Open Rate: 45.2% (-3% ↘️)
• Click Rate: 8.3% (→)

📱 Instagram
• Impressions: 15,420 (+25% ↗️)
• Reach: 8,920 (+18% ↗️)
```

**How it works:**
- Metrics are automatically saved after each report
- Next week's report compares to the saved data
- Shows ↗️ for increases, ↘️ for decreases, → for no change
- First report won't have comparisons (no previous data)

## 📁 Files

- `bot_interactive.py` - Interactive bot with `/metrics` command
- `bot.py` - Updated with comparison logic and error handling
- `metrics_history.json` - Stores last week's metrics (auto-generated, gitignored)

## 🚀 Usage

### Option 1: Interactive Bot (with commands)
```bash
python3 bot_interactive.py
```
Keeps running and responds to `/metrics` commands.

### Option 2: Scheduled Reports (automatic)
```bash
python3 bot_scheduled.py
```
Sends reports every Monday at 9 AM automatically.

### Option 3: One-time Report
```bash
python3 bot.py
```
Sends reports to all clients once.

## 💡 Tips

- Run `bot_interactive.py` to enable on-demand reports
- First report won't show comparisons (no previous data)
- Metrics history is saved in `metrics_history.json` (gitignored for security)
- Error alerts help you catch API issues immediately

