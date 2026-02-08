#!/usr/bin/env python3
"""
Email sender script that can be called programmatically from Streamlit
Accepts email, subject, and message as command line arguments
"""
import sys
import smtplib
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_email(recipient_email, subject, message):
    """
    Send an email using SMTP with actual credentials from environment
    """
    print(f"Sending email to: {recipient_email}")
    print(f"Subject: {subject}")

    # Get email credentials from environment
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    sender_email = os.getenv('EMAIL_ADDRESS', 'meoahsan01@gmail.com')
    sender_password = os.getenv('EMAIL_APP_PASSWORD', 'csmp hyyv lvmh rqsz')

    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Add body to email
        msg.attach(MIMEText(message, 'plain'))

        # Create SMTP session
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable security
        server.login(sender_email, sender_password)

        # Send email
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()

        print(f"Email sent successfully to {recipient_email}")
        return True

    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def main():
    # Parse command line arguments: recipient_email, subject, message
    if len(sys.argv) != 4:
        print("Usage: python email_mcp_server.py <recipient_email> <subject> <message>")
        sys.exit(1)

    recipient_email = sys.argv[1]
    subject = sys.argv[2]
    message = sys.argv[3]

    success = send_email(recipient_email, subject, message)
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()