import os
import time
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# If you modify these scopes, make sure delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
NEEDS_ACTION_DIR = os.path.join("AI_Employee_Vault", "Needs_Action")


def get_gmail_service():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def watch_gmail():
    print("📧 Gmail Watcher started. Polling for unread emails every 30 seconds...")
    service = get_gmail_service()

    # Keep track of emails we have already processed so we don't duplicate tasks
    processed_ids = set()

    while True:
        try:
            # Search for unread emails
            results = (
                service.users().messages().list(userId="me", q="is:unread").execute()
            )
            messages = results.get("messages", [])

            for message in messages:
                msg_id = message["id"]

                if msg_id not in processed_ids:
                    msg = (
                        service.users().messages().get(userId="me", id=msg_id).execute()
                    )
                    headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}

                    subject = headers.get("Subject", "No Subject")
                    sender = headers.get("From", "Unknown")
                    snippet = msg.get("snippet", "")

                    print(f"\n📬 New unread email detected: {subject}")

                    # Create the task file for Qwen
                    filename = f"EMAIL_{msg_id}.md"
                    filepath = os.path.join(NEEDS_ACTION_DIR, filename)

                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(f"---\n")
                        f.write(f"type: email\n")
                        f.write(f"from: {sender}\n")
                        f.write(f"subject: {subject}\n")
                        f.write(f"received: {datetime.now().isoformat()}\n")
                        f.write(f"status: pending\n")
                        f.write(f"---\n\n")
                        f.write(f"## Email Content\n")
                        f.write(f"{snippet}\n\n")
                        f.write(
                            f"Task: Please process this email using your email-triage skill.\n"
                        )

                    print(f"✅ Created task file: {filename} in /Needs_Action")
                    processed_ids.add(msg_id)

            # Rest for 30 seconds before checking again
            time.sleep(30)

        except Exception as e:
            print(f"⚠️ Error checking emails: {e}")
            time.sleep(30)


if __name__ == "__main__":
    watch_gmail()
