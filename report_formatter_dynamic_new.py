"""
Fully dynamic funnel rendering - adapts to any client configuration
EXACT working format - no changes to layout
"""
from datetime import datetime, timedelta
from report_formatter import generate_action_plan
import json
import os

def get_last_week_metrics(client_id):
    """Load last week's metrics for comparison"""
    try:
        if os.path.exists('metrics_history.json'):
            with open('metrics_history.json', 'r') as f:
                history = json.load(f)
                return history.get(client_id, {})
    except:
        pass
    return {}

def get_channel_emoji(channel_type):
    """Map channel type to emoji"""
    emoji_map = {
        'social': '📱',
        'content': '📝',
        'owned': '🌐',
        'paid': '💰',
        'referral': '👥'
    }
    return emoji_map.get(channel_type, '📊')

def get_traffic_light(value, min_threshold, target_threshold):
    """Return traffic light emoji based on value"""
    if value < min_threshold:
        return '🔴'
    elif value < target_threshold:
        return '🟡'
    else:
        return '🟢'

def calculate_capture_rate(metrics):
    """Calculate capture rate from awareness to subscribers"""
    total_reach = metrics.get('total_reach', 0) or sum(metrics.get('awareness', {}).values())
    new_subs = metrics.get('capture', {}).get('new_subscribers', 0)
    if total_reach > 0:
        return (new_subs / total_reach) * 100
    return 0

def calculate_inquiry_rate(metrics):
    """Calculate inquiry rate from subscribers"""
    total_subs = metrics.get('capture', {}).get('total_subscribers', 0)
    conversion_metrics = metrics.get('conversion', {})
    inquiries = conversion_metrics.get('Inquiries', 0) or conversion_metrics.get('inquiries', 0)
    if total_subs > 0:
        return (inquiries / total_subs) * 100
    return 0

def calculate_close_rate(metrics):
    """Calculate close rate from calls to clients"""
    conversion_metrics = metrics.get('conversion', {})
    calls = conversion_metrics.get('calls_booked', 0) or conversion_metrics.get('Calls', 0)
    new_clients = conversion_metrics.get('new_clients', 0)
    if calls > 0:
        return (new_clients / calls) * 100
    return 0

def calculate_growth(current, previous):
    """Calculate percentage growth"""
    if previous == 0 or previous is None:
        return 0
    return ((current - previous) / previous) * 100

def identify_bottleneck(metrics):
    """Identify the weakest link in the funnel"""
    from report_formatter import identify_bottleneck as identify_bottleneck_base
    return identify_bottleneck_base(metrics)

def format_funnel_visual(client_data, metrics):
    """
    EXACT working format - no changes
    """
    funnel_config = client_data.get('funnel_structure', {})
    
    # Date
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    date_range = f"{start_date.strftime('%b %d')}-{end_date.strftime('%d, %Y')}"
    
    # Get metrics
    awareness_channels = funnel_config.get('awareness', {}).get('channels', [])
    total_reach = sum(metrics.get('awareness', {}).values()) or metrics.get('total_reach', 0)
    awareness_metrics = metrics.get('awareness', {})
    
    capture_metrics = metrics.get('capture', {})
    capture_rate = calculate_capture_rate(metrics)
    
    open_rate = capture_metrics.get('open_rate', 0)
    click_rate = capture_metrics.get('click_rate', 0)
    engaged = capture_metrics.get('opens', 0)
    
    inquiry_rate = calculate_inquiry_rate(metrics)
    close_rate = calculate_close_rate(metrics)
    
    inquiries = metrics.get('inquiries', 0)
    calls = metrics.get('calls_booked', 0)
    new_clients = metrics.get('new_clients', 0)
    
    conversion_metrics = metrics.get('conversion', {})
    if not inquiries:
        inquiries = conversion_metrics.get('Inquiries', 0) or conversion_metrics.get('inquiries', 0)
    if not calls:
        calls = conversion_metrics.get('calls_booked', 0) or conversion_metrics.get('Calls', 0)
    if not new_clients:
        new_clients = conversion_metrics.get('new_clients', 0)
    
    # Build channel list
    channel_lines = []
    for ch in awareness_channels:
        value = awareness_metrics.get(ch.get('name', 'Unknown'), 0)
        name = ch.get('name', 'Unknown')[:12]  # Truncate if too long
        channel_lines.append(f"┃ {name}: {value:,}")
    
    if not channel_lines:
        channel_lines.append("┃ No channels")
    
    funnel = f"""
📊 *WEEKLY FUNNEL REPORT*



{date_range}



━━━━━━━━━━━━━

┏━━━━━━━━━━┓

┃   👀 AWARENESS         

┃   {total_reach:,} people            

┃                        

{chr(10).join(channel_lines)}

┗━━━┳━━━━━━┛

         ↓ {capture_rate:.1f}%

         

    ┏━━━━━━━━━━┓

    ┃ 🧲 LEAD CAPTURE  

    ┃ {capture_metrics.get('total_subscribers', 0)} subscribers    

    ┃                  

    ┃ +{capture_metrics.get('new_subscribers', 0)} this week       

    ┗━━━━┳━━━━━┛

         ↓ {open_rate:.1f}%

         

       ┏━━━━━━━━━━┓

       ┃ 💌 ENGAGE  

       ┃ {engaged} opened     

       ┃           

       ┃ Click: {click_rate:.1f}% 

       ┗━━┳━━━━━━━┛

          ↓ {inquiry_rate:.2f}%

          

         ┏━━━━━━━┓

         ┃ 💰 $$ ┃

         ┃ {inquiries} inquire┃

         ┃ {calls} calls  ┃

         ┃ {new_clients} client{'s' if new_clients != 1 else ''} ┃

         ┗━━━━━━━┛

━━━━━━━━━━━━━━━━━━━━━━━━━━━

*FUNNEL FLOW*



{total_reach:,} saw content

  ↓ {capture_rate:.1f}%

{capture_metrics.get('total_subscribers', 0)} subscribers

  ↓ {open_rate:.1f}%

{engaged} opened emails

  ↓ {inquiry_rate:.2f}%

{inquiries} inquiries

  ↓ {close_rate:.0f}%

{new_clients} client{'s' if new_clients != 1 else ''}



Overall: {(new_clients/total_reach*100):.3f}% if total_reach > 0 else 0:.3f}%

Target: 0.01%



━━━━━━━━━━━━━

*DROP-OFF POINTS*



{get_traffic_light(capture_rate, 3, 4)} Capture: {capture_rate:.1f}% (target: 4%)

{get_traffic_light(open_rate, 35, 40)} Opens: {open_rate:.1f}% (target: 40%)

{get_traffic_light(inquiry_rate, 0.5, 1)} Inquiries: {inquiry_rate:.2f}% (target: 1.5%)

{get_traffic_light(close_rate, 30, 40)} Close: {close_rate:.0f}% (target: 40%)



🎯 Fix RED first

"""
    
    return funnel

def format_performance_analysis(metrics, last_week):
    """
    EXACT working format
    """
    blog_visitors = metrics.get('awareness', {}).get('Blog', 0) or metrics.get('blog_visitors', 0)
    ig_impressions = metrics.get('awareness', {}).get('Instagram', 0) or metrics.get('ig_impressions', 0)
    
    blog_growth = calculate_growth(blog_visitors, last_week.get('blog_visitors', blog_visitors))
    ig_growth = calculate_growth(ig_impressions, last_week.get('ig_impressions', ig_impressions))
    
    new_subs = metrics.get('capture', {}).get('new_subscribers', 0)
    new_subs_growth = calculate_growth(new_subs, last_week.get('new_subscribers', new_subs))
    
    total_reach = metrics.get('total_reach', 0) or sum(metrics.get('awareness', {}).values())
    capture_rate = calculate_capture_rate(metrics)
    open_rate = metrics.get('capture', {}).get('open_rate', 0)
    click_rate = metrics.get('capture', {}).get('click_rate', 0)
    inquiry_rate = calculate_inquiry_rate(metrics)
    close_rate = calculate_close_rate(metrics)
    total_subs = metrics.get('capture', {}).get('total_subscribers', 0)
    
    analysis = f"""

━━━━━━━━━━━━━

*PERFORMANCE*



👀 *AWARENESS* {'✅' if total_reach >= 5000 else '⚠️'}

Reach: {total_reach:,}

Blog: {blog_growth:+.0f}% vs last week

IG: {ig_growth:+.0f}% vs last week

Target: 5K+ weekly

Status: {'Above target' if total_reach >= 5000 else 'Below target'}



🧲 *CAPTURE* {'⚠️' if capture_rate < 3 else '✅'}

Rate: {capture_rate:.1f}%

New: {new_subs} ({new_subs_growth:+.0f}%)

Total: {total_subs:,}

Target: 3-5%

{'⚠️ Too many leave without signing up' if capture_rate < 3 else '✅ Good capture rate'}



💌 *ENGAGEMENT* {'✅' if open_rate >= 40 else '⚠️'}

Opens: {open_rate:.1f}%

Clicks: {click_rate:.1f}%

Target: 35-45% / 3-5%

{'✅ Content resonates well' if open_rate >= 40 else '⚠️ Content needs work'}



💰 *CONVERSION*

Inquiries: {inquiry_rate:.1f}%

Close: {close_rate:.0f}%

Target: 1-2% / 30%+

{'✅ Great closer, need more inquiries' if close_rate >= 40 and inquiry_rate < 1 else '✅ Good conversion' if close_rate >= 30 else '⚠️ Need improvement'}

"""
    return analysis

def format_bottleneck_section(metrics):
    """
    EXACT working format
    """
    bottleneck_name, _ = identify_bottleneck(metrics)
    
    blog_visitors = metrics.get('awareness', {}).get('Blog', 0) or metrics.get('blog_visitors', 0)
    total_subs = metrics.get('capture', {}).get('total_subscribers', 0)
    conversion_metrics = metrics.get('conversion', {})
    inquiries = conversion_metrics.get('Inquiries', 0) or conversion_metrics.get('inquiries', 0) or metrics.get('inquiries', 0)
    new_subs = metrics.get('capture', {}).get('new_subscribers', 0)
    
    if bottleneck_name == 'INQUIRIES':
        current = inquiries
        target = int(total_subs * 0.015)
        gap = target - current
        monthly_impact = gap * 4
        clients_impact = int(monthly_impact * 0.4)
    elif bottleneck_name == 'LEAD CAPTURE':
        current = new_subs
        target = int(blog_visitors * 0.04)
        gap = target - current
        monthly_impact = gap * 4
        clients_impact = "1-2"
    else:
        current = 0
        target = 0
        gap = 0
        monthly_impact = 0
        clients_impact = 0
    
    bottleneck = f"""

━━━━━━━━━━━━━

🎯 *THE BOTTLENECK*



Weakest: *{bottleneck_name}*

{'Not enough people reaching out' if bottleneck_name == 'INQUIRIES' else 'Too many visitors leave'}



*Math:*

Current: {current}/week

Target: {target}/week

Gap: +{gap}/week



*Impact:*

+{monthly_impact}/month

= {clients_impact} clients/month

"""
    return bottleneck

def format_whats_working(metrics):
    """
    EXACT working format
    """
    wins = []
    
    close_rate = calculate_close_rate(metrics)
    open_rate = metrics.get('capture', {}).get('open_rate', 0)
    blog_visitors = metrics.get('awareness', {}).get('Blog', 0) or metrics.get('blog_visitors', 0)
    blog_visitors_last_week = metrics.get('blog_visitors_last_week', blog_visitors)
    
    if close_rate >= 40:
        wins.append(f"🔥 {close_rate:.0f}% close (avg: 30%)")
    
    if open_rate >= 40:
        wins.append(f"🔥 {open_rate:.1f}% opens (top 10%)")
    
    blog_growth = calculate_growth(blog_visitors, blog_visitors_last_week)
    if blog_growth > 5:
        wins.append(f"🔥 Blog {blog_growth:+.0f}% growth")
    
    if not wins:
        wins.append("🔥 Consistent publishing")
    
    section = f"""

━━━━━━━━━━━━━

✅ *WHAT'S WORKING*



{chr(10).join(wins)}

"""
    return section

def format_needs_attention(metrics):
    """
    EXACT working format
    """
    issues = []
    
    blog_visitors = metrics.get('awareness', {}).get('Blog', 0) or metrics.get('blog_visitors', 0)
    capture_rate = calculate_capture_rate(metrics)
    new_subs = metrics.get('capture', {}).get('new_subscribers', 0)
    inquiry_rate = calculate_inquiry_rate(metrics)
    open_rate = metrics.get('capture', {}).get('open_rate', 0)
    
    if capture_rate < 3:
        lost = int(blog_visitors * 0.04 - new_subs)
        issues.append(f"📉 Capture: {capture_rate:.1f}% (losing ~{lost}/week)")
    
    if inquiry_rate < 1:
        issues.append(f"📉 Inquiries: {inquiry_rate:.1f}% (need more reach-outs)")
    
    if open_rate < 35:
        issues.append(f"📉 Opens: {open_rate:.1f}% (improve content)")
    
    if not issues:
        return ""
    
    section = f"""

━━━━━━━━━━━━━

⚠️ *NEEDS ATTENTION*



{chr(10).join(issues)}

"""
    return section

def format_action_plan_section(metrics):
    """
    EXACT working format
    """
    bottleneck_name, _ = identify_bottleneck(metrics)
    actions = generate_action_plan(bottleneck_name, metrics)
    
    if not actions:
        return ""
    
    p1 = actions.get('priority_1', {})
    
    section = f"""

━━━━━━━━━━━━━

🎯 *THIS WEEK'S FOCUS*



{p1.get('title', 'Optimize')}

Why: {p1.get('why', '')}

Result: {p1.get('expected', '')}

Time: {p1.get('time', '')}

Impact: {p1.get('impact', '')}

"""
    return section

def format_growth_trajectory(metrics):
    """
    EXACT working format
    """
    new_clients = metrics.get('conversion', {}).get('new_clients', 0) or metrics.get('new_clients', 0)
    blog_visitors = metrics.get('awareness', {}).get('Blog', 0) or metrics.get('blog_visitors', 0)
    
    current_month = new_clients * 4
    current_rev_low = current_month * 700
    current_rev_high = current_month * 1000
    
    target_close = 0.5
    target_month = int(blog_visitors * 4 * 0.04 * 0.015 * target_close)
    target_rev_low = target_month * 700
    target_rev_high = target_month * 1000
    
    diff = (target_rev_low - current_rev_low)
    
    section = f"""

━━━━━━━━━━━━━

📊 *PROJECTIONS*



Current path:

~{current_month} clients/month

Revenue: ${current_rev_low:,}-{int(current_rev_high/1000)}K MRR



If you hit targets:

~{target_month} clients/month

Revenue: ${target_rev_low:,}-{int(target_rev_high/1000)}K MRR



Gap: {diff:+,}/month

"""
    return section

def format_bottom_line(metrics):
    """
    EXACT working format
    """
    total_reach = metrics.get('total_reach', 0) or sum(metrics.get('awareness', {}).values())
    conversion_metrics = metrics.get('conversion', {})
    clients = conversion_metrics.get('new_clients', 0) or metrics.get('new_clients', 0)
    overall = (clients / total_reach) * 100 if total_reach > 0 else 0
    
    status = "✅ Above average" if overall > 0.01 else "⚠️ Below average"
    
    bottleneck_name, _ = identify_bottleneck(metrics)
    
    section = f"""

━━━━━━━━━━━━━

🔥 *BOTTOM LINE*



{clients} client{'s' if clients != 1 else ''} from {total_reach:,} people

= {overall:.3f}% conversion



Industry: 0.01%

You: {overall:.3f}%

{status}



Fix {bottleneck_name.lower()} first



━━━━━━━━━━━━━

"""
    return section

def generate_full_report(client_data, metrics, last_week_metrics=None):
    """
    Assemble complete report
    """
    if last_week_metrics is None:
        client_id = client_data.get('client_id', 'unknown')
        last_week_metrics = get_last_week_metrics(client_id)
    
    report = ""
    report += format_funnel_visual(client_data, metrics)
    report += format_performance_analysis(metrics, last_week_metrics)
    report += format_bottleneck_section(metrics)
    report += format_whats_working(metrics)
    report += format_needs_attention(metrics)
    report += format_action_plan_section(metrics)
    report += format_growth_trajectory(metrics)
    report += format_bottom_line(metrics)
    
    if len(report) > 4096:
        report = report[:4050] + "\n\n..."
    
    return report

