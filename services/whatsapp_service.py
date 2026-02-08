import subprocess
import sys
import os
from typing import Optional

class WhatsAppService:
    """Service class to handle WhatsApp operations"""

    @staticmethod
    def send_message(phone_number: str, message: str) -> bool:
        """
        Send WhatsApp message using the whatsapp_sender.py script

        Args:
            phone_number: Phone number to send message to
            message: Message content

        Returns:
            bool: True if message sent successfully, False otherwise
        """
        try:
            # Prepare the command to run the WhatsApp script with positional arguments
            # The script expects: phone_number, message
            cmd = [
                sys.executable,
                "whatsapp_sender.py",
                phone_number,
                message
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30  # Timeout after 30 seconds
            )

            # Check if the command executed successfully
            if result.returncode == 0:
                print(f"WhatsApp message sent successfully to {phone_number}")
                return True
            else:
                print(f"Error sending WhatsApp message: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("Error: WhatsApp sending timed out")
            return False
        except FileNotFoundError:
            print("Error: whatsapp_sender.py not found")
            return False
        except Exception as e:
            print(f"Unexpected error sending WhatsApp message: {str(e)}")
            return False

