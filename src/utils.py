"""
Environment setup and utility functions for WhatsApp Automation
"""

import os
from dotenv import load_dotenv
from whatsapp_automation import WhatsAppAutomation, manual_send_message


def load_env():
    """Load environment variables from .env file"""
    load_dotenv()


def send_test_message(phone_number: str, message: str):
    """
    Send a test message using the WhatsApp automation system
    """
    load_env()

    success = manual_send_message(phone_number, message)
    if success:
        print(f"Test message sent successfully to {phone_number}")
    else:
        print(f"Failed to send test message to {phone_number}")


def create_sample_config():
    """
    Create a sample configuration file
    """
    config_content = '''# WhatsApp Automation System
# Environment Variables Configuration

# Your whapi.cloud API token
WHAPI_TOKEN=your_whapi_cloud_token_here

# Base URL for whapi.cloud API (default: https://gate.whapi.cloud)
WHAPI_BASE_URL=https://gate.whapi.cloud

# Port for webhook server (only used if USE_WEBHOOK=true)
WEBHOOK_PORT=8000

# Polling interval in seconds (used when not using webhooks)
POLLING_INTERVAL=30

# Enable webhook mode (true/false)
USE_WEBHOOK=false
'''

    with open('.env', 'w') as f:
        f.write(config_content)

    print("Sample .env file created. Please update with your actual whapi.cloud token.")


def main():
    """Main function for utilities"""
    print("WhatsApp Automation Utilities")
    print("1. Load environment variables")
    print("2. Send test message")
    print("3. Create sample config")


if __name__ == "__main__":
    main()