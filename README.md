# Telegram Metrics Reporter Bot

Automated weekly metrics reports sent via Telegram. Fetches data from Beehiiv, Instagram, and Vercel/GA4.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Telegram Bot

1. Open Telegram, search **@BotFather**
2. Send `/newbot`
3. Name it: "Metrics Reporter" or whatever you like
4. Get your **bot token** (looks like `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### 3. Get Your Chat ID

1. Copy `.env.example` to `.env` and add your bot token:
   ```bash
   cp .env.example .env
   # Edit .env and add TELEGRAM_BOT_TOKEN
   ```

2. Run the chat ID finder:
   ```bash
   python test_chat_id.py
   ```

3. Open Telegram, find your bot, send `/start`
4. Copy the chat ID from the terminal output to `.env`

### 4. Configure API Keys

Add all your API keys to `.env`:

- **Beehiiv**: Dashboard → Settings → Integrations → API
- **Instagram**: developers.facebook.com → Create App → Instagram Graph API
- **Vercel**: Dashboard → Settings → Tokens

### 5. Set Up Clients

1. Copy `clients.json.example` to `clients.json`:
   ```bash
   cp clients.json.example clients.json
   ```

2. Edit `clients.json` with your client data:
   ```json
   {
     "clients": [
       {
         "name": "Client A",
         "chat_id": "123456789",
         "beehiiv_pub_id": "pub_xxx",
         "instagram_id": "ig_xxx",
         "vercel_project_id": "prj_xxx"
       }
     ]
   }
   ```

### 6. Test It

```bash
python bot.py
```

You should receive a message in Telegram with your weekly metrics!

## 📅 Automation Options

### Option A: Python Schedule (Local)

Run the scheduled version:

```bash
python bot_scheduled.py
```

This will send reports every Monday at 9:00 AM.

### Option B: Cron Job (VPS/Server)

```bash
# Edit crontab
crontab -e

# Add this line (every Monday at 9 AM)
0 9 * * 1 cd /path/to/soulin_social_bot && /usr/bin/python3 bot.py
```

### Option C: GitHub Actions (Free, Recommended)

See `.github/workflows/weekly-report.yml`. Add secrets in GitHub:
- Settings → Secrets → Actions
- Add all your API keys and tokens

## 📁 Project Structure

```
soulin_social_bot/
├── bot.py                 # Main bot script
├── bot_scheduled.py       # Scheduled version
├── test_chat_id.py        # Helper to find chat ID
├── clients.json           # Client configurations (create from example)
├── .env                   # Environment variables (create from example)
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🔧 API Setup Guides

### Beehiiv
1. Go to Beehiiv dashboard
2. Settings → Integrations → API
3. Create new API key
4. Add to `.env` as `BEEHIIV_API_KEY`

### Instagram Graph API
1. Go to developers.facebook.com
2. Create app → Business type
3. Add Instagram Graph API product
4. Get long-lived token (60 days)
5. Add to `.env` as `INSTAGRAM_ACCESS_TOKEN`
6. Get your Instagram User ID and add to `.env`

### Vercel Analytics
1. Vercel dashboard → Settings → Tokens
2. Create new token
3. Add to `.env` as `VERCEL_TOKEN`
4. Get project ID from your project settings

## 🎯 Features

- ✅ Multi-client support
- ✅ Weekly automated reports
- ✅ Beehiiv newsletter metrics
- ✅ Instagram insights
- ✅ Website analytics (Vercel or GA4)
- ✅ Error handling with notifications
- ✅ Beautiful formatted messages

## 🚨 Troubleshooting

**Bot not sending messages?**
- Check your bot token in `.env`
- Verify chat ID is correct
- Make sure bot is started in Telegram

**API errors?**
- Verify all API keys are correct
- Check API rate limits
- Ensure tokens haven't expired (Instagram tokens expire after 60 days)

**No data showing?**
- Check API permissions
- Verify publication/user IDs are correct
- Some APIs may require time to accumulate data

## 📝 License

Free to use and modify.


