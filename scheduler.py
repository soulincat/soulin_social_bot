"""
Auto-report scheduling system - sends reports based on client settings
"""
import schedule
import time
import json
import os
from datetime import datetime
import pytz
from bot import send_telegram_message
from metrics_collector import collect_all_metrics
from report_formatter_dynamic import generate_full_report
from utils.projects import extract_projects

def load_last_period_metrics(scope_id):
    """Load last saved metrics for comparison"""
    try:
        if os.path.exists('metrics_history.json'):
            with open('metrics_history.json', 'r') as f:
                history = json.load(f)
                return history.get(scope_id, {})
    except:
        pass
    return {}

def save_metrics(scope_id, metrics):
    """Save current metrics for next comparison"""
    try:
        history = {}
        if os.path.exists('metrics_history.json'):
            with open('metrics_history.json', 'r') as f:
                history = json.load(f)
        
        history[scope_id] = {
            'awareness': metrics.get('awareness', {}),
            'capture': metrics.get('capture', {}),
            'conversion': metrics.get('conversion', {}),
            'fans_total': metrics.get('fans_total'),
            'monthly_revenue': metrics.get('monthly_revenue'),
            'date': datetime.now().isoformat()
        }
        
        with open('metrics_history.json', 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"⚠️ Error saving metrics history: {e}")

def send_weekly_report(client_id):
    """
    Generate and send weekly report for specific client.
    """
    try:
        # Load client data
        with open('clients.json', 'r') as f:
            data = json.load(f)
        
        client = None
        for c in data['clients']:
            if c.get('client_id') == client_id:
                client = c
                break
        
        if not client:
            print(f"❌ Client {client_id} not found")
            return
        
        if client.get('status') != 'active':
            print(f"⏸️ Client {client_id} is not active")
            return
        
        projects = extract_projects(client)
        for project in projects:
            try:
                metrics = collect_all_metrics(client, project)
                scope_id = metrics.get('scope_id')
                last_week = load_last_period_metrics(scope_id)
                report = generate_full_report(client, project, metrics, last_week)
                send_telegram_message(client['chat_id'], report)
                save_metrics(scope_id, metrics)
                print(f"✅ Sent weekly report to {client.get('name', client_id)} ({project.get('project_name')})")
            except Exception as project_error:
                error_msg = f"❌ Error for {client.get('name')} / {project.get('project_name')}: {project_error}"
                print(error_msg)
                try:
                    send_telegram_message(client['chat_id'], error_msg)
                except Exception:
                    pass
        
    except Exception as e:
        print(f"❌ Error sending report to {client_id}: {e}")
        
        # Send error notification to client
        try:
            error_msg = f"⚠️ Couldn't generate your report this week. Error: {str(e)}\n\nI'll try again next week."
            send_telegram_message(client['chat_id'], error_msg)
        except:
            pass

def schedule_client_reports():
    """
    Set up automatic reports for each client based on their settings.
    """
    try:
        with open('clients.json', 'r') as f:
            data = json.load(f)
        
        scheduled_count = 0
        
        for client in data['clients']:
            if client.get('status') != 'active':
                continue
            
            settings = client.get('report_settings', {})
            client_id = client.get('client_id')
            
            if not client_id:
                print(f"⚠️ Client {client.get('name')} missing client_id, skipping")
                continue
            
            # Get client's timezone
            timezone_str = settings.get('timezone', 'UTC')
            try:
                tz = pytz.timezone(timezone_str)
            except:
                tz = pytz.UTC
            
            # Schedule based on frequency
            frequency = settings.get('frequency', 'weekly')
            
            if frequency == 'weekly':
                day = settings.get('day', 'Monday')
                time_str = settings.get('time', '09:00')
                
                # Map day name to schedule method
                day_map = {
                    'Monday': schedule.every().monday,
                    'Tuesday': schedule.every().tuesday,
                    'Wednesday': schedule.every().wednesday,
                    'Thursday': schedule.every().thursday,
                    'Friday': schedule.every().friday,
                    'Saturday': schedule.every().saturday,
                    'Sunday': schedule.every().sunday
                }
                
                day_method = day_map.get(day, schedule.every().monday)
                day_method.at(time_str).do(
                    send_weekly_report,
                    client_id=client_id
                ).tag(client_id)
                
                scheduled_count += 1
                print(f"📅 Scheduled {frequency} report for {client.get('name')} on {day} at {time_str}")
            
            elif frequency == 'daily':
                time_str = settings.get('time', '09:00')
                schedule.every().day.at(time_str).do(
                    send_weekly_report,  # Can reuse same function
                    client_id=client_id
                ).tag(client_id)
                
                scheduled_count += 1
                print(f"📅 Scheduled {frequency} report for {client.get('name')} at {time_str}")
        
        print(f"✅ Scheduled reports for {scheduled_count} clients")
        
    except Exception as e:
        print(f"❌ Error setting up schedules: {e}")

def run_scheduler():
    """
    Main loop that runs the scheduler continuously.
    """
    print("🤖 Starting report scheduler...")
    
    # Initial setup
    schedule_client_reports()
    
    # Run forever
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute
        
        # Re-sync schedules every 24 hours (in case client settings changed)
        current_time = datetime.now()
        if current_time.hour == 0 and current_time.minute == 0:
            schedule.clear()
            schedule_client_reports()
            print("🔄 Resynced client schedules")

if __name__ == "__main__":
    # For testing
    run_scheduler()

