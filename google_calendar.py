import os
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import pytz

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class GoogleCalendarClient:
    def __init__(self, calendar_id='primary', timezone='America/New_York'):
        self.calendar_id = calendar_id
        self.timezone = pytz.timezone(timezone)
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        creds = None
        
        if os.path.exists('token.json'):
            with open('token.json', 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                # Request offline access to get a refresh token that doesn't expire
                creds = flow.run_local_server(port=0, access_type='offline', prompt='consent')
            
            with open('token.json', 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('calendar', 'v3', credentials=creds)
    
    def get_today_events(self):
        now = datetime.datetime.now(self.timezone)
        return self.get_events_for_date(now)
    
    def get_all_calendars(self):
        try:
            calendars = self.service.calendarList().list().execute()
            return calendars.get('items', [])
        except Exception as e:
            print(f"Error fetching calendar list: {e}")
            return []
    
    def get_events_for_date(self, date):
        if isinstance(date, str):
            date = datetime.datetime.strptime(date, '%Y-%m-%d')
        
        if date.tzinfo is None:
            date = self.timezone.localize(date)
        
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + datetime.timedelta(days=1)
        
        time_min = start_of_day.isoformat()
        time_max = end_of_day.isoformat()
        
        all_events = []
        
        calendars = self.get_all_calendars()
        calendar_ids = [cal['id'] for cal in calendars]
        
        for cal_id in calendar_ids:
            try:
                events_result = self.service.events().list(
                    calendarId=cal_id,
                    timeMin=time_min,
                    timeMax=time_max,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                
                events = events_result.get('items', [])
                
                # Add calendar name to each event for context
                calendar_name = cal_id
                for calendar in self.get_all_calendars():
                    if calendar['id'] == cal_id:
                        calendar_name = calendar.get('summary', cal_id)
                        break
                
                for event in events:
                    event['calendar_name'] = calendar_name
                
                all_events.extend(events)
            except Exception as e:
                print(f"Error fetching events from calendar {cal_id}: {e}")
                continue
        
        # Sort all events by start time
        parsed_events = self._parse_events(all_events)
        min_datetime = self.timezone.localize(datetime.datetime(1900, 1, 1))
        parsed_events.sort(key=lambda x: x.get('start_time', min_datetime))
        
        return parsed_events
    
    def _parse_events(self, events):
        parsed_events = []
        
        for event in events:
            event_data = {
                'summary': event.get('summary', 'No title'),
                'location': event.get('location', ''),
                'description': event.get('description', ''),
                'calendar_name': event.get('calendar_name', ''),
            }
            
            if 'dateTime' in event.get('start', {}):
                start_str = event['start']['dateTime']
                event_data['start_time'] = datetime.datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                event_data['all_day'] = False
            elif 'date' in event.get('start', {}):
                naive_date = datetime.datetime.strptime(event['start']['date'], '%Y-%m-%d')
                event_data['start_time'] = self.timezone.localize(naive_date)
                event_data['all_day'] = True
            
            if 'dateTime' in event.get('end', {}):
                end_str = event['end']['dateTime']
                event_data['end_time'] = datetime.datetime.fromisoformat(end_str.replace('Z', '+00:00'))
            elif 'date' in event.get('end', {}):
                naive_date = datetime.datetime.strptime(event['end']['date'], '%Y-%m-%d')
                event_data['end_time'] = self.timezone.localize(naive_date)
            
            parsed_events.append(event_data)
        
        return parsed_events