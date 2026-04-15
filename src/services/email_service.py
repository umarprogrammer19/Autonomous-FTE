import subprocess
import sys
import os

# Resolve script path relative to this service file's grandparent (src/)
_SERVICE_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.dirname(_SERVICE_DIR)
_EMAIL_SCRIPT = os.path.join(_SRC_DIR, "email_mcp_server.py")

class EmailService:
    """Service class to handle email operations"""

    @staticmethod
    def send_email(recipient_email: str, subject: str, message: str) -> bool:
        """
        Send email using the email_mcp_server.py script

        Args:
            recipient_email: Email address to send to
            subject: Email subject
            message: Email message content

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Prepare the command to run the email script with positional arguments
            # The script expects: recipient_email, subject, message
            cmd = [
                sys.executable,  # Use the same Python interpreter
                _EMAIL_SCRIPT,
                recipient_email,
                subject,
                message
            ]

            # Execute the email script
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30  # Timeout after 30 seconds
            )

            # Check if the command executed successfully
            if result.returncode == 0:
                print(f"Email sent successfully to {recipient_email}")
                return True
            else:
                print(f"Error sending email: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("Error: Email sending timed out")
            return False
        except FileNotFoundError:
            print("Error: email_mcp_server.py not found")
            return False
        except Exception as e:
            print(f"Unexpected error sending email: {str(e)}")
            return False