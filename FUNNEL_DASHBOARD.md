# Funnel Dashboard Guide

## Overview

The dashboard now tracks your marketing funnel from awareness to conversion, organized into four stages:

1. **🎯 AWARENESS** - Top of funnel traffic
2. **🧲 LEAD CAPTURE** - Email signups
3. **💌 NURTURE** - Newsletter engagement
4. **💰 CONVERSION** - Inquiries, calls, clients

## Funnel Stages

### 🎯 Awareness
Tracks where people first discover you:
- **Blog Visitors** - From Vercel Analytics (automatic)
- **Instagram Impressions** - From Instagram API (automatic)
- **LinkedIn Impressions** - Manual entry via `/update` command

### 🧲 Lead Capture
Tracks email list growth:
- **New Subscribers** - This week's new signups (manual or calculated)
- **Total Subscribers** - From Beehiiv API (automatic)
- **Conversion Rate** - Blog visitors → Email signups (auto-calculated)

### 💌 Nurture
Tracks newsletter engagement:
- **Open Rate** - From Beehiiv API (automatic)
- **Click Rate** - From Beehiiv API (automatic)

### 💰 Conversion
Tracks revenue-generating actions:
- **Inquiries** - Form submissions (manual entry)
- **Calls Booked** - Discovery calls scheduled (manual entry)
- **New Clients** - Retainer signups (manual entry)
- **Conversion Rates** - Auto-calculated between stages

## Manual Metrics Tracking

### Available Metrics

You can manually update these metrics via Telegram:

- `inquiries` - Number of inquiry form submissions
- `calls_booked` - Discovery calls scheduled
- `retainer_signups` - New client signups
- `linkedin_impressions` - LinkedIn post impressions
- `new_subscribers` - New email subscribers this week

### How to Update

Send a command to your bot:
```
/update inquiries 2
/update calls_booked 1
/update retainer_signups 1
/update linkedin_impressions 890
/update new_subscribers 23
```

The bot will save these to `manual_metrics.json` for the current week.

### Automatic Calculation

If you don't manually enter `new_subscribers`, the bot will calculate it by comparing current total subscribers to last week's total.

## Conversion Rates

The dashboard automatically calculates conversion rates:

- **Blog → Email**: `(new_subscribers / blog_visitors) * 100`
- **Email → Inquiry**: `(inquiries / total_subscribers) * 100`
- **Inquiry → Call**: `(calls_booked / inquiries) * 100`
- **Call → Client**: `(retainer_signups / calls_booked) * 100`

## Weekly Reports

### Telegram Commands

- `/metrics` or `/funnel` - Get your weekly funnel report
- `/update <metric> <value>` - Update a manual metric
- `/start` - Show help message

### Automated Reports

The bot sends weekly reports every Monday at 9 AM with:
- All funnel stage metrics
- Conversion rates between stages
- Week-over-week comparisons (when available)

## Data Storage

- **manual_metrics.json** - Stores manual tracking data (week-based)
- **metrics_history.json** - Stores API metrics for comparison

Both files are gitignored for security.

## Example Workflow

1. **Monday morning**: Bot sends weekly report
2. **Throughout week**: Update manual metrics as events happen
   ```
   /update inquiries 1
   /update calls_booked 1
   ```
3. **End of week**: Review funnel performance
4. **Next Monday**: Compare to previous week

## Tips

- Update manual metrics as events happen (don't wait until end of week)
- The bot tracks metrics by week (Monday to Sunday)
- First report won't have comparisons (no previous data)
- Conversion rates help identify bottlenecks in your funnel

