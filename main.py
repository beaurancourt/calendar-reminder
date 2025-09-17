#!/usr/bin/env python3

import os
import time
import schedule
import pytz
from datetime import datetime, timedelta
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
            tz = pytz.timezone(timezone)
            events = calendar_client.get_events_for_date(datetime.now(tz))

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
        error_msg = str(e)
        print(f"[{datetime.now()}] Error in send_daily_summary: {error_msg}")

        # Try to send error to Pushover
        try:
            pushover_client = PushoverClient(
                user_key=os.getenv('PUSHOVER_USER_KEY'),
                api_token=os.getenv('PUSHOVER_API_TOKEN')
            )
            pushover_client.send_summary(
                title="❌ Calendar Summary Error",
                message=f"Failed to generate calendar summary:\n\n{error_msg}"
            )
        except Exception as pushover_error:
            print(f"[{datetime.now()}] Failed to send error to Pushover: {pushover_error}")

def send_tomorrow_summary():
    print(f"[{datetime.now()}] Generating calendar summary for tomorrow...")
    print(f"[{datetime.now()}] Including events from ALL calendars...")

    try:
        timezone = os.getenv('TIMEZONE', 'America/New_York')
        calendar_id = os.getenv('GOOGLE_CALENDAR_ID', 'primary')

        calendar_client = GoogleCalendarClient(calendar_id=calendar_id, timezone=timezone)

        # Get tomorrow's date
        tz = pytz.timezone(timezone)
        tomorrow = datetime.now(tz) + timedelta(days=1)
        events = calendar_client.get_events_for_date(tomorrow)

        summary_gen = SummaryGenerator(timezone=timezone)
        message = summary_gen.generate_summary(events)

        pushover_client = PushoverClient(
            user_key=os.getenv('PUSHOVER_USER_KEY'),
            api_token=os.getenv('PUSHOVER_API_TOKEN')
        )

        title = f"📅 Tomorrow's Calendar ({tomorrow.strftime('%A, %B %d')})"
        success = pushover_client.send_summary(
            title=title,
            message=message
        )

        if success:
            print(f"[{datetime.now()}] Tomorrow's summary sent successfully!")
        else:
            print(f"[{datetime.now()}] Failed to send tomorrow's summary")

    except Exception as e:
        error_msg = str(e)
        print(f"[{datetime.now()}] Error in send_tomorrow_summary: {error_msg}")

        # Try to send error to Pushover
        try:
            pushover_client = PushoverClient(
                user_key=os.getenv('PUSHOVER_USER_KEY'),
                api_token=os.getenv('PUSHOVER_API_TOKEN')
            )
            pushover_client.send_summary(
                title="❌ Tomorrow's Calendar Error",
                message=f"Failed to generate tomorrow's calendar summary:\n\n{error_msg}"
            )
        except Exception as pushover_error:
            print(f"[{datetime.now()}] Failed to send error to Pushover: {pushover_error}")

def run_scheduler():
    timezone = pytz.timezone(os.getenv('TIMEZONE', 'America/New_York'))
    summary_time = os.getenv('SUMMARY_TIME', '08:00')
    tomorrow_summary_time = os.getenv('TOMORROW_SUMMARY_TIME', '22:00')

    schedule.every().day.at(summary_time).do(send_daily_summary)
    schedule.every().day.at(tomorrow_summary_time).do(send_tomorrow_summary)

    print(f"Calendar reminder service started!")
    print(f"Timezone: {timezone}")
    print(f"Daily summary scheduled for: {summary_time}")
    print(f"Tomorrow's summary scheduled for: {tomorrow_summary_time}")
    print(f"Press Ctrl+C to stop\n")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

def test_summary(test_date=None, tomorrow=False):
    if tomorrow:
        print("Testing calendar summary generation for tomorrow...")
        send_tomorrow_summary()
    elif test_date:
        print(f"Testing calendar summary generation for {test_date}...")
        send_daily_summary(test_date)
    else:
        print("Testing calendar summary generation for today...")
        send_daily_summary()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_date = None
        tomorrow = False

        # Parse remaining arguments
        args = sys.argv[2:]
        for arg in args:
            if arg == "tomorrow":
                tomorrow = True
            elif not test_date and '-' not in arg[:2]:  # Assume it's a date if not a flag
                test_date = arg

        test_summary(test_date, tomorrow)
    else:
        try:
            run_scheduler()
        except KeyboardInterrupt:
            print(f"\n[{datetime.now()}] Service stopped by user")
        except Exception as e:
            print(f"[{datetime.now()}] Service error: {e}")