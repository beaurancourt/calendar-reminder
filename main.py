#!/usr/bin/env python3

import os
import time
import schedule
import pytz
from datetime import datetime
from dotenv import load_dotenv

from google_calendar import GoogleCalendarClient
from pushover_client import PushoverClient
from summary_generator import SummaryGenerator

load_dotenv()

def send_daily_summary(test_date=None):
    if test_date:
        print(f"[{datetime.now()}] Generating calendar summary for {test_date}...")
    else:
        print(f"[{datetime.now()}] Generating daily calendar summary...")
    
    print(f"[{datetime.now()}] Including events from ALL calendars...")
    
    try:
        timezone = os.getenv('TIMEZONE', 'America/New_York')
        calendar_id = os.getenv('GOOGLE_CALENDAR_ID', 'primary')
        
        calendar_client = GoogleCalendarClient(calendar_id=calendar_id, timezone=timezone)
        
        if test_date:
            events = calendar_client.get_events_for_date(test_date)
        else:
            events = calendar_client.get_events_for_date(datetime.now())
        
        summary_gen = SummaryGenerator(timezone=timezone)
        message = summary_gen.generate_summary(events)
        
        pushover_client = PushoverClient(
            user_key=os.getenv('PUSHOVER_USER_KEY'),
            api_token=os.getenv('PUSHOVER_API_TOKEN')
        )
        
        title = f"📅 Calendar Summary for {test_date}" if test_date else "📅 Daily Calendar Summary"
        success = pushover_client.send_summary(
            title=title,
            message=message
        )
        
        if success:
            print(f"[{datetime.now()}] Summary sent successfully!")
        else:
            print(f"[{datetime.now()}] Failed to send summary")
            
    except Exception as e:
        print(f"[{datetime.now()}] Error in send_daily_summary: {e}")

def run_scheduler():
    timezone = pytz.timezone(os.getenv('TIMEZONE', 'America/New_York'))
    summary_time = os.getenv('SUMMARY_TIME', '08:00')
    
    schedule.every().day.at(summary_time).do(send_daily_summary)
    
    print(f"Calendar reminder service started!")
    print(f"Timezone: {timezone}")
    print(f"Daily summary scheduled for: {summary_time}")
    print(f"Press Ctrl+C to stop\n")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

def test_summary(test_date=None):
    if test_date:
        print(f"Testing calendar summary generation for {test_date}...")
    else:
        print("Testing calendar summary generation for today...")
    send_daily_summary(test_date)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_date = None
        
        # Parse remaining arguments
        args = sys.argv[2:]
        for arg in args:
            if not test_date and '-' not in arg[:2]:  # Assume it's a date if not a flag
                test_date = arg
        
        test_summary(test_date)
    else:
        try:
            run_scheduler()
        except KeyboardInterrupt:
            print(f"\n[{datetime.now()}] Service stopped by user")
        except Exception as e:
            print(f"[{datetime.now()}] Service error: {e}")