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
                creds = flow.run_local_server(port=0)
            
            with open('token.json', 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('calendar', 'v3', credentials=creds)
    
    def get_today_events(self):
        now = datetime.datetime.now(self.timezone)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + datetime.timedelta(days=1)
        
        time_min = start_of_day.isoformat()
        time_max = end_of_day.isoformat()
        
        try:
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            return self._parse_events(events)
        except Exception as e:
            print(f"Error fetching calendar events: {e}")
            return []
    
    def _parse_events(self, events):
        parsed_events = []
        
        for event in events:
            event_data = {
                'summary': event.get('summary', 'No title'),
                'location': event.get('location', ''),
                'description': event.get('description', ''),
            }
            
            if 'dateTime' in event.get('start', {}):
                start_str = event['start']['dateTime']
                event_data['start_time'] = datetime.datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                event_data['all_day'] = False
            elif 'date' in event.get('start', {}):
                event_data['start_time'] = datetime.datetime.strptime(event['start']['date'], '%Y-%m-%d')
                event_data['all_day'] = True
            
            if 'dateTime' in event.get('end', {}):
                end_str = event['end']['dateTime']
                event_data['end_time'] = datetime.datetime.fromisoformat(end_str.replace('Z', '+00:00'))
            elif 'date' in event.get('end', {}):
                event_data['end_time'] = datetime.datetime.strptime(event['end']['date'], '%Y-%m-%d')
            
            parsed_events.append(event_data)
        
        return parsed_events