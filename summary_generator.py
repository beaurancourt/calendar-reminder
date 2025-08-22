import datetime
import pytz

class SummaryGenerator:
    def __init__(self, timezone='America/New_York'):
        self.timezone = pytz.timezone(timezone)
    
    def generate_summary(self, events):
        if not events:
            return self._no_events_message()
        
        now = datetime.datetime.now(self.timezone)
        date_str = now.strftime('%A, %B %d, %Y')
        
        message_parts = [f"<b>Your schedule for {date_str}</b>\n"]
        
        all_day_events = [e for e in events if e.get('all_day', False)]
        timed_events = [e for e in events if not e.get('all_day', False)]
        
        if all_day_events:
            message_parts.append("\n<b>All-day events:</b>")
            for event in all_day_events:
                message_parts.append(f"• {event['summary']}")
                if event.get('location'):
                    message_parts.append(f"  📍 {event['location']}")
        
        if timed_events:
            message_parts.append("\n<b>Scheduled events:</b>")
            for event in sorted(timed_events, key=lambda x: x['start_time']):
                time_str = self._format_time_range(event)
                message_parts.append(f"• {time_str}: {event['summary']}")
                if event.get('location'):
                    message_parts.append(f"  📍 {event['location']}")
        
        event_count = len(events)
        message_parts.append(f"\n<i>Total: {event_count} event{'s' if event_count != 1 else ''} today</i>")
        
        return '\n'.join(message_parts)
    
    def _format_time_range(self, event):
        start_time = event['start_time']
        end_time = event.get('end_time')
        
        if hasattr(start_time, 'astimezone'):
            start_time = start_time.astimezone(self.timezone)
        if end_time and hasattr(end_time, 'astimezone'):
            end_time = end_time.astimezone(self.timezone)
        
        start_str = start_time.strftime('%-I:%M %p')
        
        if end_time:
            if end_time.date() == start_time.date():
                end_str = end_time.strftime('%-I:%M %p')
                return f"{start_str} - {end_str}"
            else:
                return f"{start_str} (multi-day)"
        
        return start_str
    
    def _no_events_message(self):
        now = datetime.datetime.now(self.timezone)
        date_str = now.strftime('%A, %B %d, %Y')
        return f"<b>Your schedule for {date_str}</b>\n\nNo events scheduled for today. Enjoy your free day! 🎉"