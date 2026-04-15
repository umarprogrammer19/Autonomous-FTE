import os
import pickle
import time
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import markdown
from dotenv import load_dotenv

load_dotenv()

# Scopes for Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailWatcher:
    """
    Gmail Watcher script to monitor new emails and create .md files in Needs_Action folder
    """

    def __init__(self, vault_path="C:/Users/AHSEN/Desktop/hackathon_0/AI_Employee_Vault"):
        self.vault_path = vault_path
        self.needs_action_path = os.path.join(vault_path, "Needs_Action")
        self.credentials_path = os.path.join(vault_path, "gmail_credentials.json")
        self.token_path = os.path.join(vault_path, "token.pickle")
        self.service = None

    def authenticate(self):
        """Authenticate with Gmail API"""
        creds = None

        # Load existing token
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)

        # If there are no valid credentials, request authorization
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('gmail', 'v1', credentials=creds)

    def get_recent_emails(self, days=1):
        """Get emails from the last specified number of days"""
        # Calculate the date threshold
        threshold_date = (datetime.now() - timedelta(days=days)).strftime('%Y/%m/%d')

        # Search for emails received after the threshold date
        query = f'after:{threshold_date}'
        results = self.service.users().messages().list(
            userId='me',
            q=query,
            maxResults=10  # Limit to 10 most recent emails
        ).execute()

        messages = results.get('messages', [])
        return messages

    def get_email_details(self, msg_id):
        """Get details of a specific email"""
        msg = self.service.users().messages().get(userId='me', id=msg_id).execute()

        # Extract headers
        headers = {header['name']: header['value'] for header in msg['payload']['headers']}

        # Extract body
        body = ""
        if 'parts' in msg['payload']:
            for part in msg['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    import base64
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
        else:
            import base64
            body = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')

        return {
            'id': msg_id,
            'subject': headers.get('Subject', 'No Subject'),
            'from': headers.get('From', 'Unknown Sender'),
            'date': headers.get('Date', ''),
            'body': body[:2000]  # Limit body length
        }

    def create_markdown_file(self, email_data):
        """Create a markdown file in Needs_Action folder"""
        filename = f"gmail_{email_data['id']}_{int(time.time())}.md"
        filepath = os.path.join(self.needs_action_path, filename)

        # Create markdown content
        md_content = f"""# Gmail Notification: {email_data['subject']}

## Email Details
- **From:** {email_data['from']}
- **Date:** {email_data['date']}
- **ID:** {email_data['id']}

## Email Body
{email_data['body']}

## Action Required
- [ ] Review email content
- [ ] Determine appropriate response
- [ ] Take necessary action
- [ ] Update status to completed

---
*Created by Gmail Watcher on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        # Write the markdown file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"Created file: {filepath}")

    def watch_and_process(self):
        """Main function to watch for new emails and create markdown files"""
        # Create Needs_Action directory if it doesn't exist
        os.makedirs(self.needs_action_path, exist_ok=True)

        # Authenticate with Gmail
        try:
            self.authenticate()
        except Exception as e:
            print(f"Authentication failed: {e}")
            print("Please ensure you have set up Gmail API credentials correctly.")
            return

        # Get recent emails
        messages = self.get_recent_emails(days=1)
        print(f"Found {len(messages)} recent emails")

        # Process each email
        for msg in messages:
            try:
                email_data = self.get_email_details(msg['id'])

                # Check if we already processed this email
                existing_files = [f for f in os.listdir(self.needs_action_path) if f.startswith(f"gmail_{msg['id']}")]

                if not existing_files:
                    self.create_markdown_file(email_data)
                    print(f"Processed email: {email_data['subject']}")
                else:
                    print(f"Skipped already processed email: {email_data['subject']}")

            except Exception as e:
                print(f"Error processing email {msg['id']}: {e}")

    def run(self):
        """Run the Gmail watcher continuously"""
        print("Starting Gmail Watcher...")
        while True:
            try:
                self.watch_and_process()
                print("Waiting 300 seconds (5 minutes) before next check...")
                time.sleep(300)  # Wait 5 minutes before next check
            except KeyboardInterrupt:
                print("Gmail Watcher stopped by user")
                break
            except Exception as e:
                print(f"Error in Gmail Watcher: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

if __name__ == "__main__":
    # Set up the Gmail watcher
    watcher = GmailWatcher()
    watcher.run()