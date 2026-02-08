"""
Simple WhatsApp Message Sender using whapi.cloud API
Takes user input for name and message, matches to predefined contacts, and sends via whapi.cloud
"""

import os
import requests
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('whatsapp_sender.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WhatsAppSender:
    def __init__(self):
        # Load credentials from environment variables
        self.api_token = os.getenv('WHAPI_TOKEN', "0IvyJHVeWVDSfrjUn4PYJb7xVPxlXxjW")
        self.api_url_base = os.getenv('WHAPI_BASE_URL', 'https://gate.whapi.cloud')

        if not self.api_token or self.api_token == 'your_actual_whapi_cloud_token_here':
            raise ValueError("WHAPI_TOKEN environment variable is required and must be set to your actual whapi.cloud token")

        # Fixed contact list
        self.contacts = {
            'ahsen': '923182710120',
            'adil': '923118059734'
        }

        # Headers for API requests
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_token}"
        }

        logger.info("WhatsApp Sender initialized")

    def match_contact(self, name):
        """Match name to phone number"""
        name_lower = name.lower().strip()
        if name_lower in self.contacts:
            return self.contacts[name_lower]
        return None

    def send_whatsapp_message(self, phone_number, message):
        """Send a WhatsApp message using whapi.cloud API"""
        try:
            url = f"{self.api_url_base}/messages/text"

            payload = {
                "typing_time": 0,
                "to": phone_number,
                "body": message
            }

            response = requests.post(url, json=payload, headers=self.headers)

            if response.status_code in [200, 201]:
                logger.info(f"Message sent successfully to {phone_number}")
                return True, response.text
            else:
                logger.error(f"Failed to send message: {response.status_code} - {response.text}")
                return False, response.text

        except Exception as e:
            logger.error(f"Error sending message to {phone_number}: {str(e)}")
            return False, str(e)

    def send_message_to_contact(self, name, message):
        """Send message to contact by name"""
        phone_number = self.match_contact(name)

        if not phone_number:
            logger.error(f"Contact '{name}' not found in contact list")
            print(f"Contact '{name}' not found in contact list")
            print(f"Available contacts: {', '.join(self.contacts.keys())}")
            return False

        logger.info(f"Sending message to {name} ({phone_number}): {message}")
        print(f"Sending message to {name} ({phone_number})...")

        success, response = self.send_whatsapp_message(phone_number, message)

        if success:
            logger.info(f"[SUCCESS] Message sent to {name} ({phone_number})")
            print(f"[SUCCESS] Message sent to {name} ({phone_number})")
        else:
            logger.error(f"[FAILED] Could not send message to {name} ({phone_number})")
            print(f"[FAILED] Could not send message to {name} ({phone_number})")

        # Log detailed information
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'name': name,
            'number': phone_number,
            'message': message,
            'status': 'SUCCESS' if success else 'FAILED',
            'response': response
        }

        logger.info(f"LOG_ENTRY: {log_entry}")

        return success

def main():
    """Main function to run the WhatsApp sender"""
    print("WhatsApp Message Sender")
    print("=" * 30)

    try:
        sender = WhatsAppSender()
    except ValueError as e:
        print(f"[ERROR] Error: {e}")
        print("Please make sure to set your WHAPI_TOKEN in the .env file")
        return

    print("Available contacts:")
    for name, number in sender.contacts.items():
        print(f"  - {name}: {number}")
    print()

    # Get user input
    name = input("Enter contact name: ").strip()
    message = input("Enter message: ").strip()

    if not name or not message:
        print("Both name and message are required!")
        return

    # Send the message
    sender.send_message_to_contact(name, message)

if __name__ == "__main__":
    main()