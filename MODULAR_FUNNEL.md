# 🎯 Modular Funnel System

The bot now supports **fully customizable, modular funnel structures** for each client. No more hardcoded assumptions!

## 🚀 Key Features

### 1. **Dynamic Awareness Channels**
- Add unlimited channels (Blog, Instagram, LinkedIn, TikTok, Podcast, etc.)
- Each channel can be auto-tracked (API) or manual entry
- Automatic emoji assignment based on channel type
- Mobile-optimized display (shows top 3 channels)

### 2. **Flexible Conversion Touchpoints**
- Multiple conversion paths (calls, webinars, forms, DMs, carts)
- Each tracked independently
- Supports any business model

### 3. **Product Flexibility**
- Unlimited products/services
- Different pricing models (one-time, monthly, annual)
- Revenue tracking per product

### 4. **Custom Benchmarks**
- Industry-specific targets
- Client-adjustable goals
- Traffic light system (red/yellow/green)

## 📋 Client Structure

```json
{
  "client_id": "client_xxx",
  "name": "Client Name",
  "chat_id": "123456789",
  
  "funnel_structure": {
    "awareness": {
      "channels": [
        {
          "name": "Blog",
          "type": "owned",
          "tracking": "auto",
          "source": "vercel",
          "metric_name": "blog_visitors"
        },
        {
          "name": "Instagram",
          "type": "social",
          "tracking": "auto",
          "source": "instagram",
          "metric_name": "ig_impressions"
        },
        {
          "name": "Podcast",
          "type": "content",
          "tracking": "manual",
          "metric_name": "podcast_reach"
        }
      ]
    },
    "capture": {
      "platform": "Beehiiv",
      "method": "Lead magnet",
      "description": "Free ebook download"
    },
    "nurture": {
      "method": "Newsletter",
      "frequency": "weekly",
      "platform": "Beehiiv"
    },
    "conversion": {
      "touchpoints": [
        {
          "name": "Discovery call",
          "type": "call",
          "tracking": "manual",
          "metric_name": "calls_booked"
        }
      ]
    },
    "products": [
      {
        "name": "1:1 Coaching",
        "price": 2000,
        "billing": "monthly",
        "type": "service"
      }
    ]
  }
}
```

## 🔄 Migration

Existing clients are automatically migrated to the new structure:

```bash
python3 migrate_clients.py
```

This creates a backup and converts your existing `clients.json` to the new format while preserving all data.

## 📊 Channel Types & Emojis

- `social` → 📱 (Instagram, TikTok, LinkedIn)
- `content` → 📝 (Blog, Podcast, YouTube)
- `owned` → 🌐 (Website, Email)
- `paid` → 💰 (Ads, Sponsored)
- `referral` → 👥 (Word of mouth)
- `event` → 🎤 (Webinars, Live events)

## 🛠️ Adding New Channels

### Via clients.json:
```json
{
  "name": "TikTok",
  "type": "social",
  "tracking": "manual",
  "metric_name": "tiktok_views"
}
```

### Manual Metric Entry:
```bash
/update tiktok_views 5000
```

## 🎨 Dynamic Report Rendering

The report automatically adapts to each client's funnel:

- **Awareness**: Shows all configured channels with their metrics
- **Capture**: Displays the configured platform (Beehiiv, ConvertKit, etc.)
- **Nurture**: Shows method and frequency
- **Conversion**: Lists all touchpoints
- **Products**: Displays configured products

## 🔙 Backward Compatibility

The system maintains full backward compatibility:

- Old `clients.json` structure still works
- Legacy fields preserved in `_legacy` object
- Automatic fallback to defaults if new structure missing

## 📝 Example: Different Business Types

### Coach:
- Awareness: LinkedIn, Podcast, Blog
- Capture: Lead magnet → Email
- Conversion: Discovery calls
- Products: Retainer, Group program

### Artist:
- Awareness: Instagram, Pinterest, Portfolio
- Capture: Newsletter signup
- Conversion: DM inquiries → Commissions
- Products: Custom artwork, Prints

### E-commerce:
- Awareness: Instagram, TikTok, Ads
- Capture: Email popup
- Conversion: Cart → Checkout
- Products: Physical products, Digital downloads

## 🚀 Next Steps

1. **Run migration**: `python3 migrate_clients.py`
2. **Customize your funnel**: Edit `clients.json` to match your business
3. **Add channels**: Add any awareness channels you use
4. **Configure products**: List all your offerings
5. **Set benchmarks**: Adjust targets in `custom_benchmarks`

The bot will automatically adapt to your unique funnel structure!

