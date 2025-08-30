import os
import json
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from flask import session, request, url_for
import exchangelib
import requests
import urllib.parse

class GoogleCalendarService:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        self.CLIENT_CONFIG = {
            "web": {
                "client_id": "YOUR_CLIENT_ID",
                "client_secret": "YOUR_CLIENT_SECRET",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost:6922/auth/google/callback"]
            }
        }
    
    def get_authorization_url(self):
        """Get Google OAuth authorization URL"""
        flow = Flow.from_client_config(
            self.CLIENT_CONFIG,
            scopes=self.SCOPES,
            redirect_uri=url_for('calendar.google_callback', _external=True)
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        session['state'] = state
        return authorization_url
    
    def exchange_code_for_token(self, authorization_code, state):
        """Exchange authorization code for access token"""
        if session.get('state') != state:
            raise Exception('Invalid state parameter')
        
        flow = Flow.from_client_config(
            self.CLIENT_CONFIG,
            scopes=self.SCOPES,
            redirect_uri=url_for('calendar.google_callback', _external=True)
        )
        
        flow.fetch_token(code=authorization_code)
        
        credentials = flow.credentials
        session['google_credentials'] = credentials_to_dict(credentials)
        
        return credentials
    
    def get_events(self, time_min=None, time_max=None, max_results=50):
        """Get events from Google Calendar"""
        if 'google_credentials' not in session:
            raise Exception('No credentials available')
        
        credentials = Credentials(**session['google_credentials'])
        
        # Refresh token if expired
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            session['google_credentials'] = credentials_to_dict(credentials)
        
        service = build('calendar', 'v3', credentials=credentials)
        
        # Default time range: next 30 days
        if not time_min:
            time_min = datetime.utcnow().isoformat() + 'Z'
        if not time_max:
            time_max = (datetime.utcnow() + timedelta(days=30)).isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Convert to our format
        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            # Handle all-day events
            if 'T' not in start:
                start += 'T00:00:00'
                end += 'T23:59:59'
            
            formatted_event = {
                'title': event.get('summary', 'No Title'),
                'description': event.get('description', 'Imported from Google Calendar'),
                'start_time': start.replace('T', ' ').split('+')[0].split('Z')[0],
                'end_time': end.replace('T', ' ').split('+')[0].split('Z')[0],
                'location': event.get('location', ''),
                'attendees': [attendee.get('email', '') for attendee in event.get('attendees', [])],
                'platform': self._determine_platform(event.get('location', ''), event.get('description', '')),
                'google_event_id': event['id']
            }
            
            formatted_events.append(formatted_event)
        
        return formatted_events
    
    def _determine_platform(self, location, description):
        """Determine meeting platform from location/description"""
        text = (location + ' ' + description).lower()
        
        if 'teams' in text or 'microsoft teams' in text:
            return 'Microsoft Teams'
        elif 'zoom' in text:
            return 'Zoom'
        elif 'google meet' in text or 'meet.google' in text:
            return 'Google Meet'
        elif any(word in text for word in ['phone', 'call', 'dial']):
            return 'Phone Call'
        elif any(word in text for word in ['http', 'www', '.com']):
            return 'Other'
        else:
            return 'In Person'

def credentials_to_dict(credentials):
    """Convert credentials to dictionary for session storage"""
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

class OutlookCalendarService:
    def __init__(self):
        self.CLIENT_ID = "YOUR_OUTLOOK_CLIENT_ID"
        self.CLIENT_SECRET = "YOUR_OUTLOOK_CLIENT_SECRET"
        self.REDIRECT_URI = "http://localhost:6922/auth/outlook/callback"
        self.SCOPES = ["https://graph.microsoft.com/calendars.read"]
    
    def get_authorization_url(self):
        """Get Microsoft OAuth authorization URL"""
        params = {
            'client_id': self.CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': self.REDIRECT_URI,
            'scope': ' '.join(self.SCOPES),
            'response_mode': 'query'
        }
        
        return f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?{urllib.parse.urlencode(params)}"
    
    def exchange_code_for_token(self, authorization_code):
        """Exchange authorization code for access token"""
        data = {
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET,
            'code': authorization_code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.REDIRECT_URI
        }
        
        response = requests.post('https://login.microsoftonline.com/common/oauth2/v2.0/token', data=data)
        token_data = response.json()
        
        if 'access_token' in token_data:
            session['outlook_credentials'] = token_data
            return token_data
        else:
            raise Exception(f"Error getting token: {token_data}")
    
    def get_events(self):
        """Get events from Outlook Calendar"""
        if 'outlook_credentials' not in session:
            raise Exception('No credentials available')
        
        access_token = session['outlook_credentials']['access_token']
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Get events for next 30 days
        start_time = datetime.utcnow().isoformat()
        end_time = (datetime.utcnow() + timedelta(days=30)).isoformat()
        
        url = f"https://graph.microsoft.com/v1.0/me/calendar/calendarView"
        params = {
            'startDateTime': start_time,
            'endDateTime': end_time,
            '$top': 50
        }
        
        response = requests.get(url, headers=headers, params=params)
        events_data = response.json()
        
        if 'value' not in events_data:
            raise Exception(f"Error fetching events: {events_data}")
        
        # Convert to our format
        formatted_events = []
        for event in events_data['value']:
            start = event['start']['dateTime']
            end = event['end']['dateTime']
            
            formatted_event = {
                'title': event.get('subject', 'No Title'),
                'description': event.get('body', {}).get('content', 'Imported from Outlook Calendar'),
                'start_time': start.replace('T', ' ').split('.')[0],
                'end_time': end.replace('T', ' ').split('.')[0],
                'location': event.get('location', {}).get('displayName', ''),
                'attendees': [attendee.get('emailAddress', {}).get('address', '') for attendee in event.get('attendees', [])],
                'platform': self._determine_platform(event.get('location', {}).get('displayName', ''), event.get('body', {}).get('content', '')),
                'outlook_event_id': event['id']
            }
            
            formatted_events.append(formatted_event)
        
        return formatted_events
    
    def _determine_platform(self, location, description):
        """Determine meeting platform from location/description"""
        text = (location + ' ' + description).lower()
        
        if 'teams' in text or 'microsoft teams' in text:
            return 'Microsoft Teams'
        elif 'zoom' in text:
            return 'Zoom'
        elif 'google meet' in text:
            return 'Google Meet'
        elif any(word in text for word in ['phone', 'call']):
            return 'Phone Call'
        elif any(word in text for word in ['http', 'www']):
            return 'Other'
        else:
            return 'In Person'