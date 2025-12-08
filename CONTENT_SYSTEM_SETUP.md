# Content System Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install the `anthropic` package for Claude API integration.

### 2. Configure Environment Variables

Add to your `.env` file:

```bash
ANTHROPIC_API_KEY=your_claude_api_key_here
```

Get your API key from: https://console.anthropic.com/

### 3. Start the Web Server

```bash
python3 app.py
```

Then navigate to:
- Dashboard: http://localhost:3000/
- Content Hub: http://localhost:3000/content

### 4. Start Telegram Bot (Optional)

```bash
python3 bot_interactive.py
```

Use commands:
- `/content create <your idea>` - Create a new post
- `/content list` - List all posts
- `/content pillars` - View pillar performance

### 5. Set Up Publishing Scheduler (Optional)

To automatically publish scheduled content, run:

```bash
python3 content_scheduler.py
```

Or add to cron (runs every 5 minutes):
```bash
*/5 * * * * cd /path/to/soulin_social_bot && python3 content_scheduler.py
```

## First Steps

1. **Create a Content Pillar** (via web interface or API)
   - Go to `/content` and create your first post
   - Pillars can be created via API: `POST /api/content/pillars`

2. **Create Your First Post**
   - Use `/content create "Your idea here"` on Telegram
   - Or use the web form at `/content/create`

3. **Generate Branches**
   - After creating a post, generate archive and blog versions
   - Click "Generate Archive & Blog" on the post detail page

4. **Generate Derivatives**
   - Create newsletter, social posts, and Telegram announcements
   - Click "Generate All Derivatives" on the post detail page

5. **Schedule Publishing**
   - Set publish times for your derivatives
   - The scheduler will automatically publish them

## Data Files

All content data is stored in JSON files:
- `content_posts.json` - Your center posts
- `content_derivatives.json` - Generated content for publishing
- `content_metrics.json` - Performance tracking
- `content_pillars.json` - Pillar definitions

These files are automatically created when you first use the system.

## Integration with Funnel Dashboard

Content performance is automatically included in weekly reports:
- Top performing pillars
- Recent posts and their impact
- Pillar balance recommendations

The content system integrates seamlessly with your existing funnel tracking.

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
- Make sure you've added the key to your `.env` file
- Restart the application after adding the key

### "ModuleNotFoundError: No module named 'anthropic'"
- Run: `pip install -r requirements.txt`

### Content not appearing in reports
- Make sure you've tracked performance for your posts
- Use the API: `POST /api/content/posts/<id>/performance`

## Next Steps

See `CONTENT_SYSTEM_IMPLEMENTATION.md` for full documentation.

