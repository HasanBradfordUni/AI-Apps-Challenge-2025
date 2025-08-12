from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib import flow
import json
from datetime import datetime, timedelta
import exchangelib

class GoogleCalendarService:
    def __init__(self, credentials_json):
        self.credentials = Credentials.from_authorized_user_info(json.loads(credentials_json))
        self.service = build('calendar', 'v3', credentials=self.credentials)
    
    def get_events(self, time_min=None, time_max=None):
        """Retrieve events from Google Calendar"""
        if not time_min:
            time_min = datetime.utcnow().isoformat() + 'Z'
        if not time_max:
            time_max = (datetime.utcnow() + timedelta(days=30)).isoformat() + 'Z'
        
        events_result = self.service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        return events_result.get('items', [])
    
    def create_event(self, event_data):
        """Create a new event in Google Calendar"""
        event = {
            'summary': event_data.get('title'),
            'description': event_data.get('description'),
            'start': {
                'dateTime': event_data.get('start_time'),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': event_data.get('end_time'),
                'timeZone': 'UTC',
            },
            'attendees': [{'email': email} for email in event_data.get('attendees', [])],
        }
        
        if event_data.get('location'):
            event['location'] = event_data.get('location')
        
        return self.service.events().insert(calendarId='primary', body=event).execute()

class OutlookCalendarService:
    def __init__(self, credentials):
        # Initialize Exchange/Outlook connection
        self.account = exchangelib.Account(
            primary_smtp_address=credentials['email'],
            credentials=exchangelib.Credentials(
                username=credentials['username'],
                password=credentials['password']
            ),
            autodiscover=True
        )
    
    def get_events(self, time_min=None, time_max=None):
        """Retrieve events from Outlook Calendar"""
        if not time_min:
            time_min = datetime.now()
        if not time_max:
            time_max = datetime.now() + timedelta(days=30)
        
        items = self.account.calendar.filter(
            start__gte=time_min,
            start__lt=time_max
        )
        
        return [self._convert_to_dict(item) for item in items]
    
    def create_event(self, event_data):
        """Create a new event in Outlook Calendar"""
        item = exchangelib.CalendarItem(
            account=self.account,
            folder=self.account.calendar,
            subject=event_data.get('title'),
            body=event_data.get('description'),
            start=datetime.fromisoformat(event_data.get('start_time')),
            end=datetime.fromisoformat(event_data.get('end_time')),
        )
        
        if event_data.get('location'):
            item.location = event_data.get('location')
        
        if event_data.get('attendees'):
            item.required_attendees = event_data.get('attendees')
        
        item.save()
        return item
    
    def _convert_to_dict(self, item):
        """Convert Exchange item to dictionary"""
        return {
            'id': item.id,
            'subject': item.subject,
            'body': str(item.body),
            'start': item.start.isoformat(),
            'end': item.end.isoformat(),
            'location': item.location,
        }