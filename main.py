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

def send_daily_summary():
    print(f"[{datetime.now()}] Generating daily calendar summary...")
    
    try:
        timezone = os.getenv('TIMEZONE', 'America/New_York')
        calendar_id = os.getenv('GOOGLE_CALENDAR_ID', 'primary')
        
        calendar_client = GoogleCalendarClient(calendar_id=calendar_id, timezone=timezone)
        events = calendar_client.get_today_events()
        
        summary_gen = SummaryGenerator(timezone=timezone)
        message = summary_gen.generate_summary(events)
        
        pushover_client = PushoverClient(
            user_key=os.getenv('PUSHOVER_USER_KEY'),
            api_token=os.getenv('PUSHOVER_API_TOKEN')
        )
        
        success = pushover_client.send_summary(
            title="📅 Daily Calendar Summary",
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

def test_summary():
    print("Testing calendar summary generation...")
    send_daily_summary()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_summary()
    else:
        try:
            run_scheduler()
        except KeyboardInterrupt:
            print("\n[{datetime.now()}] Service stopped by user")
        except Exception as e:
            print(f"[{datetime.now()}] Service error: {e}")