"""
Detailed report formatter with interpretations, benchmarks, and actionable insights
"""
import json
from datetime import datetime, timedelta

def calculate_growth(current, previous):
    """Calculate percentage growth"""
    if previous == 0 or previous is None:
        return 0
    return ((current - previous) / previous) * 100

def get_status_emoji(value, benchmark_low, benchmark_high):
    """Return status emoji based on benchmark"""
    if value >= benchmark_high:
        return "✅"
    elif value >= benchmark_low:
        return "→"
    else:
        return "⚠️"

def interpret_metric(metric_name, value, benchmark_low, benchmark_high, context=""):
    """Generate interpretation for a metric"""
    interpretations = {
        'awareness': {
            'above': f"Your content is getting seen consistently. {context}",
            'mid': f"Steady reach. {context}",
            'below': f"Need more visibility. {context}"
        },
        'lead_capture': {
            'above': f"Excellent conversion! You're capturing emails effectively. {context}",
            'mid': f"Decent capture rate, but room to grow. {context}",
            'below': f"Traffic is good, but too many visitors leave without subscribing. You're losing potential clients here. {context}"
        },
        'engagement': {
            'above': f"Your email content resonates. People trust you and want to learn more. {context}",
            'mid': f"Good engagement. Content is relevant. {context}",
            'below': f"Content might not be resonating. Need to improve email quality. {context}"
        },
        'conversion': {
            'above': f"You're amazing at closing! {context}",
            'mid': f"Solid close rate. {context}",
            'below': f"Need to improve sales process or qualify leads better. {context}"
        }
    }
    
    if value >= benchmark_high:
        level = 'above'
    elif value >= benchmark_low:
        level = 'mid'
    else:
        level = 'below'
    
    return interpretations.get(metric_name, {}).get(level, "")

def identify_bottleneck(metrics):
    """Identify the weakest link in the funnel"""
    # Define performance scores (0-100)
    scores = {
        'awareness': min(100, (metrics.get('total_reach', 0) / 5000) * 100),
        'lead_capture': min(100, (metrics.get('capture_rate', 0) / 4) * 100),
        'engagement': min(100, (metrics.get('open_rate', 0) / 40) * 100),
        'conversion_inquiry': min(100, (metrics.get('inquiry_rate', 0) / 1.5) * 100),
        'conversion_close': min(100, (metrics.get('close_rate', 0) / 40) * 100)
    }
    
    # Find lowest score
    bottleneck = min(scores, key=scores.get)
    
    bottleneck_map = {
        'awareness': ('AWARENESS', 'Not enough people seeing your content'),
        'lead_capture': ('LEAD CAPTURE', 'Too many visitors leaving without subscribing'),
        'engagement': ('ENGAGEMENT', 'People not opening or clicking your emails'),
        'conversion_inquiry': ('INQUIRIES', 'Not enough people reaching out'),
        'conversion_close': ('CLOSE RATE', 'Not converting calls to clients')
    }
    
    return bottleneck_map.get(bottleneck, ('UNKNOWN', ''))

def generate_action_plan(bottleneck, metrics):
    """Generate specific action plan based on bottleneck"""
    actions = {
        'LEAD CAPTURE': {
            'priority_1': {
                'title': 'Add ebook popup to blog',
                'why': 'Captures emails from the 98% who currently leave',
                'expected': f"{metrics.get('capture_rate', 0):.1f}% → 4% = double your signups",
                'time': '1 hour setup',
                'impact': f"+{int(metrics.get('blog_visitors', 0) * 0.04 - metrics.get('new_subscribers', 0))} subscribers/week = +$700-1K/month revenue"
            },
            'priority_2': {
                'title': 'Add exit-intent popup',
                'why': 'Catches people as they leave',
                'expected': 'Additional 1-2% capture',
                'time': '30 min setup',
                'impact': f"+{int(metrics.get('blog_visitors', 0) * 0.015)} subscribers/week"
            }
        },
        'ENGAGEMENT': {
            'priority_1': {
                'title': 'Improve email subject lines',
                'why': 'More opens = more chances to convert',
                'expected': f"{metrics.get('open_rate', 0):.1f}% → 45% open rate",
                'time': '15 min per email',
                'impact': f"+{int(metrics.get('total_subscribers', 0) * 0.1)} more readers per email"
            },
            'priority_2': {
                'title': 'Add clear CTAs in emails',
                'why': 'Guide readers to take action',
                'expected': f"{metrics.get('click_rate', 0):.1f}% → 5% click rate",
                'time': '10 min per email',
                'impact': 'More traffic to conversion pages'
            }
        },
        'INQUIRIES': {
            'priority_1': {
                'title': 'Add case studies to newsletter',
                'why': 'Triggers "I need this too" moment',
                'expected': f"{metrics.get('inquiry_rate', 0):.1f}% → 1% inquiry rate",
                'time': '30 min to write',
                'impact': f"+{int(metrics.get('total_subscribers', 0) * 0.01 - metrics.get('inquiries', 0))} inquiries/week"
            },
            'priority_2': {
                'title': 'Add testimonials to every email',
                'why': 'Social proof builds trust',
                'expected': 'More confidence to reach out',
                'time': '5 min per email',
                'impact': 'Higher inquiry rate'
            }
        },
        'CLOSE RATE': {
            'priority_1': {
                'title': 'Record your calls and analyze objections',
                'why': 'Learn what stops people from signing',
                'expected': f"{metrics.get('close_rate', 0):.0f}% → 50% close rate",
                'time': '1 hour review weekly',
                'impact': 'More clients from same inquiries'
            },
            'priority_2': {
                'title': 'Create call preparation checklist',
                'why': 'Consistent process = better results',
                'expected': 'More confident sales calls',
                'time': '30 min to create',
                'impact': 'Higher close rate'
            }
        },
        'AWARENESS': {
            'priority_1': {
                'title': 'Post 3x per week on Instagram',
                'why': 'More content = more reach',
                'expected': f"{metrics.get('ig_impressions', 0):,} → {int(metrics.get('ig_impressions', 0) * 1.5):,} impressions",
                'time': '2 hours/week',
                'impact': f"+{int(metrics.get('ig_impressions', 0) * 0.5):,} more people seeing your work"
            },
            'priority_2': {
                'title': 'Guest post on 1 relevant blog/month',
                'why': 'Tap into existing audiences',
                'expected': '+500-1000 new visitors',
                'time': '3 hours per post',
                'impact': 'New audience discovery'
            }
        }
    }
    
    return actions.get(bottleneck, {})

def get_channel_emoji(channel_type):
    """Get emoji for channel type"""
    emoji_map = {
        'social': '📱',
        'content': '📝',
        'owned': '🌐',
        'paid': '💰',
        'referral': '👥',
        'event': '🎤'
    }
    return emoji_map.get(channel_type, '📊')

def format_funnel_visual(metrics, client_data=None):
    """Generate custom funnel structure - mobile optimized, dynamically renders channels"""
    
    # Get client's funnel structure (defaults if not provided)
    if client_data is None:
        client_data = {}
    
    funnel_config = client_data.get('funnel_structure', {})
    
    # AWARENESS channels - dynamic from config
    awareness_channels = funnel_config.get('awareness', {}).get('channels', [])
    
    # If no channels defined, use legacy defaults
    if not awareness_channels:
        awareness_channels = [
            {'name': 'Blog', 'type': 'owned', 'metric_name': 'blog_visitors'},
            {'name': 'Instagram', 'type': 'social', 'metric_name': 'ig_impressions'},
            {'name': 'LinkedIn', 'type': 'social', 'metric_name': 'linkedin_impressions'}
        ]
    
    # LEAD CAPTURE
    capture_config = funnel_config.get('capture', {})
    capture_platform = capture_config.get('platform', 'Beehiiv')
    
    # NURTURE
    nurture_config = funnel_config.get('nurture', {})
    nurture_method = nurture_config.get('method', 'Newsletter')
    
    # CONVERSION touchpoints
    conversion_config = funnel_config.get('conversion', {})
    conversion_touchpoints = conversion_config.get('touchpoints', [])
    
    # PRODUCTS
    products = funnel_config.get('products', [])
    if not products:
        products = [{'name': 'Retainer'}]
    
    # Date
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    date_range = f"{start_date.strftime('%b %d')}-{end_date.strftime('%d, %Y')}"
    
    # Metrics
    total_reach = metrics.get('total_reach', 0)
    subscribers = metrics.get('total_subscribers', 0)
    engaged = metrics.get('opens', 0)
    inquiries = metrics.get('inquiries', 0)
    clients = metrics.get('new_clients', 0)
    
    capture_pct = metrics.get('capture_rate', 0)
    engage_pct = metrics.get('open_rate', 0)
    inquiry_pct = metrics.get('inquiry_rate', 0)
    close_pct = metrics.get('close_rate', 0)
    
    # Build awareness section dynamically (max 3 channels for mobile)
    awareness_lines = []
    for channel in awareness_channels[:3]:  # Limit to 3 for mobile
        channel_name = channel.get('name', 'Unknown')
        channel_type = channel.get('type', 'content')
        metric_name = channel.get('metric_name', '')
        emoji = get_channel_emoji(channel_type)
        
        # Get metric value
        metric_value = metrics.get(metric_name, 0)
        
        # Format: "│ 📱 IG: 5,678"
        display_name = channel_name[:8]  # Shorten for mobile
        awareness_lines.append(f"│ {emoji} {display_name}: {metric_value:,}")
    
    # Build conversion section dynamically
    conversion_lines = []
    calls_booked = metrics.get('calls_booked', 0)
    for touchpoint in conversion_touchpoints[:2]:  # Limit to 2 for mobile
        tp_name = touchpoint.get('name', 'Call')
        tp_type = touchpoint.get('type', 'call')
        metric_name = touchpoint.get('metric_name', 'calls_booked')
        
        metric_value = metrics.get(metric_name, 0)
        if metric_value > 0:
            conversion_lines.append(f"│ {metric_value} {tp_name[:10]}")
    
    # If no conversion lines, add default
    if not conversion_lines and calls_booked > 0:
        conversion_lines.append(f"│ {calls_booked} calls")
    
    # Build products section dynamically
    products_lines = []
    for product in products[:2]:  # Limit to 2 for mobile
        if isinstance(product, dict):
            product_name = product.get('name', 'Product')
        else:
            product_name = str(product)
        products_lines.append(f"│ {product_name[:15]}")
    
    # Format numbers to fit 20 char width
    total_reach_str = f"{total_reach:,}"[:18]
    subscribers_str = f"{subscribers:,}"[:18]
    engaged_str = f"{engaged}"[:18]
    inquiries_str = f"{inquiries}"
    clients_str = f"{clients}"
    capture_platform_str = capture_platform[:15]
    nurture_str = nurture_method[:6]
    
    funnel = f"""
📊 *WEEKLY FUNNEL REPORT*

{date_range}

━━━━━━━━━━━━━━━━━━━━━

┌────────────────────┐
│ 👀 AWARENESS       │
│ {total_reach_str:18s} │
│                    │
{chr(10).join(awareness_lines)}
└──────────┬─────────┘
           ↓ {capture_pct:.1f}%
           
      ┌─────────────┐
      │ 🧲 CAPTURE  │
      │ {subscribers_str:18s} │
      │             │
      │ {capture_platform_str:15s} │
      └──────┬──────┘
             ↓ {engage_pct:.1f}%
             
        ┌─────────┐
        │ 💌 {nurture_str:6s}│
        │ {engaged_str:18s} │
        └────┬────┘
             ↓ {inquiry_pct:.2f}%
             
          ┌───────┐
          │ 🎯 CV │
          │ {inquiries_str:6s} inq │
          │       │
{chr(10).join(conversion_lines) if conversion_lines else '│       │'}
          └───┬───┘
              ↓ {close_pct:.0f}%
              
            ┌───┐
            │ 💰│
            │ {clients_str:3s} │
            │   │
{chr(10).join(products_lines) if products_lines else '│   │'}
            └───┘

━━━━━━━━━━━━━━━━━━━━━

*FUNNEL FLOW*

{total_reach:,} → {subscribers:,} → {engaged} → {inquiries} → {clients}

*DROP-OFFS*

{'🔴' if capture_pct < 3 else '🟡' if capture_pct < 4 else '🟢'} Cap: {capture_pct:.1f}% (→4%)
{'🔴' if engage_pct < 35 else '🟡' if engage_pct < 40 else '🟢'} Open: {engage_pct:.1f}% (→40%)
{'🔴' if inquiry_pct < 0.5 else '🟡' if inquiry_pct < 1 else '🟢'} Inq: {inquiry_pct:.2f}% (→1.5%)
{'🔴' if close_pct < 30 else '🟡' if close_pct < 40 else '🟢'} Close: {close_pct:.0f}% (→40%)

Overall: {((clients/total_reach*100) if total_reach > 0 else 0.000):.3f}%
Target: 0.01%
"""
    return funnel

def format_performance_analysis(metrics, last_week, client_data=None):
    """Ultra-condensed for mobile - dynamically shows awareness channels"""
    
    if client_data is None:
        client_data = {}
    
    funnel_config = client_data.get('funnel_structure', {})
    awareness_channels = funnel_config.get('awareness', {}).get('channels', [])
    
    # Build awareness growth line dynamically
    awareness_growth_parts = []
    if not awareness_channels:
        # Legacy: show blog and IG
        blog_growth = calculate_growth(metrics.get('blog_visitors', 0), last_week.get('blog_visitors', metrics.get('blog_visitors', 0)))
        ig_growth = calculate_growth(metrics.get('ig_impressions', 0), last_week.get('ig_impressions', metrics.get('ig_impressions', 0)))
        awareness_growth_parts.append(f"Blog: {blog_growth:+.0f}%")
        awareness_growth_parts.append(f"IG: {ig_growth:+.0f}%")
    else:
        # Dynamic: show growth for each channel (max 3 for mobile)
        for channel in awareness_channels[:3]:
            channel_name = channel.get('name', 'Unknown')
            metric_name = channel.get('metric_name', '')
            current = metrics.get(metric_name, 0)
            previous = last_week.get(metric_name, current)
            growth = calculate_growth(current, previous)
            short_name = channel_name[:6]  # Shorten for mobile
            awareness_growth_parts.append(f"{short_name}: {growth:+.0f}%")
    
    awareness_growth_str = " | ".join(awareness_growth_parts)
    
    reach_status = '✅' if metrics.get('total_reach', 0) >= 5000 else '⚠️'
    capture_status = '✅' if metrics.get('capture_rate', 0) >= 3 else '⚠️'
    open_status = '✅' if metrics.get('open_rate', 0) >= 40 else '⚠️'
    
    analysis = f"""
━━━━━━━━━━━━━━━━━━━━━

*PERFORMANCE*

👀 *AWARENESS* {reach_status}
Reach: {metrics.get('total_reach', 0):,}
{awareness_growth_str}
Target: 5K+ weekly

🧲 *CAPTURE* {capture_status}
Rate: {metrics.get('capture_rate', 0):.1f}%
New: {metrics.get('new_subscribers', 0)} | Total: {metrics.get('total_subscribers', 0):,}
Target: 3-5%

💌 *ENGAGE* {open_status}
Open: {metrics.get('open_rate', 0):.1f}% | Click: {metrics.get('click_rate', 0):.1f}%
Target: 40% / 5%

💰 *CONVERSION*
Inq: {metrics.get('inquiry_rate', 0):.1f}% | Close: {metrics.get('close_rate', 0):.0f}%
Target: 1.5% / 40%
"""
    return analysis

def format_bottleneck_section(metrics):
    """Minimal bottleneck"""
    bottleneck_name, bottleneck_desc = identify_bottleneck(metrics)
    
    if bottleneck_name == 'LEAD CAPTURE':
        lost = int(metrics.get('blog_visitors', 0) * 0.04 - metrics.get('new_subscribers', 0))
        impact = f"+{lost}/week = 1-2 clients/mo"
    elif bottleneck_name == 'INQUIRIES':
        lost = int(metrics.get('total_subscribers', 0) * 0.015 - metrics.get('inquiries', 0))
        impact = f"+{lost}/week = +clients"
    else:
        lost = 0
        impact = "Optimize"
    
    bottleneck = f"""
━━━━━━━━━━━━━━━━━━━━━

🎯 *BOTTLENECK*

*{bottleneck_name}*

Fix this first
Impact: {impact}
"""
    return bottleneck

def format_whats_working(metrics):
    """Ultra-condensed wins"""
    wins = []
    
    if metrics.get('close_rate', 0) >= 40:
        wins.append(f"🔥 {metrics.get('close_rate', 0):.0f}% close (avg: 30%)")
    if metrics.get('open_rate', 0) >= 40:
        wins.append(f"🔥 {metrics.get('open_rate', 0):.1f}% opens (top 10%)")
    
    blog_growth = calculate_growth(metrics.get('blog_visitors', 0), metrics.get('blog_visitors_last_week', metrics.get('blog_visitors', 0)))
    if blog_growth > 5:
        wins.append(f"🔥 Blog +{blog_growth:.0f}% growth")
    
    if not wins:
        wins.append("🔥 Consistent publishing")
    
    wins_text = "\n".join(wins)
    
    section = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ *WHAT'S WORKING*

{wins_text}
"""
    return section

def format_needs_attention(metrics):
    """Ultra-condensed issues"""
    issues = []
    
    if metrics.get('capture_rate', 0) < 3:
        lost = int(metrics.get('blog_visitors', 0) * 0.04 - metrics.get('new_subscribers', 0))
        issues.append(f"📉 Capture: {metrics.get('capture_rate', 0):.1f}% (losing ~{lost}/week)")
    
    if metrics.get('inquiry_rate', 0) < 1:
        issues.append(f"📉 Inquiries: {metrics.get('inquiry_rate', 0):.1f}% (need more reach-outs)")
    
    if metrics.get('open_rate', 0) < 35:
        issues.append(f"📉 Opens: {metrics.get('open_rate', 0):.1f}% (improve content)")
    
    if not issues:
        return ""
    
    issues_text = "\n".join(issues)
    
    section = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ *NEEDS ATTENTION*

{issues_text}
"""
    return section

def format_action_plan_section(metrics):
    """Minimal action"""
    bottleneck_name, _ = identify_bottleneck(metrics)
    actions = generate_action_plan(bottleneck_name, metrics)
    
    if not actions:
        return ""
    
    p1 = actions.get('priority_1', {})
    
    section = f"""
━━━━━━━━━━━━━━━━━━━━━

🎯 *THIS WEEK*

*{p1.get('title', 'Optimize')}*

{p1.get('why', '')}

Impact: {p1.get('impact', '')}
Time: {p1.get('time', '')}
"""
    return section

def format_growth_trajectory(metrics):
    """Condensed growth projection"""
    
    current_month = metrics.get('new_clients', 0) * 4
    current_rev = f"${current_month * 700:,.0f}-{current_month}K"
    
    target_close = 0.5
    target_month = int(metrics.get('blog_visitors', 0) * 4 * 0.04 * 0.015 * target_close)
    target_rev = f"${target_month * 700:,.0f}-{target_month}K"
    
    diff = f"+${(target_month - current_month) * 700:,.0f}"
    
    section = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 *PROJECTIONS*

Current path:
~{current_month} clients/month
Revenue: {current_rev} MRR

If you hit targets:
~{target_month} clients/month
Revenue: {target_rev} MRR

*Gap: {diff}/month*
"""
    return section

def format_bottom_line(metrics):
    """Minimal summary"""
    total_reach = metrics.get('total_reach', 0)
    clients = metrics.get('new_clients', 0)
    overall = (clients / total_reach) * 100 if total_reach > 0 else 0
    
    status = "✅" if overall > 0.01 else "⚠️"
    
    bottleneck_name, _ = identify_bottleneck(metrics)
    
    section = f"""
━━━━━━━━━━━━━━━━━━━━━

🔥 *RESULT*

{clients} client{'s' if clients != 1 else ''} from {total_reach:,}
= {overall:.3f}% {status}

Fix {bottleneck_name.lower()}
━━━━━━━━━━━━━━━━━━━━━
"""
    return section

def format_detailed_report(metrics, last_week=None, client_data=None):
    """Mobile-optimized report under 4096 chars - supports dynamic funnels"""
    if last_week is None:
        last_week = {}
    
    if client_data is None:
        client_data = {}
    
    # Add last week data for growth calculations
    metrics['blog_visitors_last_week'] = last_week.get('blog_visitors', metrics.get('blog_visitors', 0))
    
    # Build report with dynamic rendering
    report = ""
    report += format_funnel_visual(metrics, client_data)
    report += format_performance_analysis(metrics, last_week, client_data)
    report += format_bottleneck_section(metrics)
    report += format_action_plan_section(metrics)
    report += format_bottom_line(metrics)
    
    # Truncate if needed
    if len(report) > 4096:
        report = report[:4050] + "\n\n..."
    
    return report

