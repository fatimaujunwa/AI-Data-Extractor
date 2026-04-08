import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def connect_gmail():
    """Connect to Gmail API and return service"""
    creds = None
    
    # Check if token already exists
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If no valid credentials, ask user to login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    service = build('gmail', 'v1', credentials=creds)
    print("✅ Connected to Gmail successfully")
    return service

def fetch_emails(service, max_emails=10):
    """Fetch recent unread emails from Gmail"""
    print(f"\n📧 Fetching last {max_emails} unread emails...")
    
    results = service.users().messages().list(
        userId='me',
        labelIds=['INBOX'],
        q='is:unread',
        maxResults=max_emails
    ).execute()
    
    messages = results.get('messages', [])
    
    if not messages:
        print("No unread emails found. Fetching recent emails instead...")
        results = service.users().messages().list(
            userId='me',
            labelIds=['INBOX'],
            maxResults=max_emails
        ).execute()
        messages = results.get('messages', [])
    
    emails = []
    
    for msg in messages:
        email_data = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='full'
        ).execute()
        
        # Extract subject
        headers = email_data['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
        
        # Extract body
        body = extract_body(email_data['payload'])
        
        emails.append({
            'id': msg['id'],
            'subject': subject,
            'sender': sender,
            'date': date,
            'body': body[:1000]  # Limit to 1000 chars
        })
    #this is the end of the function
    
    print(f"✅ Fetched {len(emails)} emails")
    return emails

def extract_body(payload):
    """Extract text body from email payload"""
    body = ""
    
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    break
    else:
        data = payload['body'].get('data', '')
        if data:
            body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    
    return body.strip()