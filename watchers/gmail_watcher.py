"""
Gmail Watcher
Monitors Gmail for new unread emails and creates action items.
Marks emails as read after processing.
"""

import os
import base64
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from base_watcher import BaseWatcher


# Gmail API scopes - need modify to mark as read
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


class GmailWatcher(BaseWatcher):
    """Watches Gmail for new unread emails."""
    
    def __init__(self, vault_path: str, credentials_path: str = 'credentials.json', check_interval: int = 120):
        """
        Initialize the Gmail watcher.
        
        Args:
            vault_path: Path to the Obsidian vault
            credentials_path: Path to Gmail API credentials
            check_interval: Seconds between checks (default: 120)
        """
        super().__init__(vault_path, check_interval)
        
        self.credentials_path = Path(credentials_path)
        self.token_path = self.credentials_path.parent / 'token.json'
        
        # Track processed email IDs
        self.processed_ids: set = set()
        
        # Connect to Gmail
        self.service = self._get_gmail_service()
        
        self.logger.info('Gmail watcher initialized')
    
    def _get_gmail_service(self):
        """
        Authenticate and return Gmail API service.
        
        Returns:
            Gmail API service object
        """
        creds = None
        
        # Load existing token
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save token for next run
            self.token_path.write_text(creds.to_json())
        
        return build('gmail', 'v1', credentials=creds)
    
    def _mark_as_read(self, message_id: str):
        """
        Mark an email as read by removing UNREAD label.
        
        Args:
            message_id: Gmail message ID
        """
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            self.logger.info(f'Marked email {message_id} as read')
        except Exception as e:
            self.logger.error(f'Error marking email as read: {e}')
    
    def check_for_updates(self) -> list:
        """
        Check Gmail for new unread emails.
        
        Returns:
            List of new email messages
        """
        new_emails = []
        
        try:
            # Get unread emails
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])
            
            for msg in messages:
                if msg['id'] not in self.processed_ids:
                    # Get full message details
                    full_msg = self.service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='full'
                    ).execute()
                    new_emails.append(full_msg)
        
        except Exception as e:
            self.logger.error(f'Error fetching emails: {e}')
        
        return new_emails
    
    def _get_header(self, headers: list, name: str) -> str:
        """
        Extract header value from email headers.
        
        Args:
            headers: List of header dictionaries
            name: Header name to find
            
        Returns:
            Header value or 'Unknown'
        """
        for header in headers:
            if header['name'].lower() == name.lower():
                return header['value']
        return 'Unknown'
    
    def _get_body(self, payload: dict) -> str:
        """
        Extract email body from payload.
        
        Args:
            payload: Email payload dictionary
            
        Returns:
            Email body text
        """
        body = ''
        
        if 'body' in payload and payload['body'].get('data'):
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        elif 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain' and part['body'].get('data'):
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
        
        return body[:1000] if body else '[No body content]'
    
    def create_action_file(self, item: dict) -> Path:
        """
        Create action file for an email and mark it as read.
        
        Args:
            item: Email message dictionary
            
        Returns:
            Path to the created action file
        """
        headers = item['payload']['headers']
        
        sender = self._get_header(headers, 'From')
        subject = self._get_header(headers, 'Subject')
        date = self._get_header(headers, 'Date')
        body = self._get_body(item['payload'])
        snippet = item.get('snippet', '')
        
        # Determine priority based on keywords
        priority = 'normal'
        priority_keywords = ['urgent', 'asap', 'important', 'invoice', 'payment', 'order']
        if any(kw in subject.lower() or kw in snippet.lower() for kw in priority_keywords):
            priority = 'high'
        
        content = f"""---
type: email
from: {sender}
subject: {subject}
date: {date}
received: {self.get_timestamp()}
priority: {priority}
status: pending
gmail_id: {item['id']}
---

## Email Content

**From:** {sender}
**Subject:** {subject}
**Date:** {date}

### Message

{body}

## Suggested Actions

- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Create task from email
- [ ] Archive after processing
"""
        
        # Create safe filename
        safe_subject = "".join(c for c in subject[:30] if c.isalnum() or c in (' ', '-', '_')).strip()
        action_filename = f"EMAIL_{safe_subject}_{item['id'][:8]}.md"
        action_path = self.needs_action / action_filename
        action_path.write_text(content)
        
        # Mark email as read in Gmail
        self._mark_as_read(item['id'])
        
        # Mark as processed locally
        self.processed_ids.add(item['id'])
        
        return action_path


if __name__ == '__main__':
    import sys
    
    # Get vault path from command line or use default
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = '../../AI_Employee_Vault'
    
    # Start watcher
    watcher = GmailWatcher(vault_path)
    watcher.run()