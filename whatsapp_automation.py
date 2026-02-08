"""
WhatsApp Automation System using whapi.cloud API

This system watches for incoming WhatsApp messages and automatically replies
to AI-related messages using Claude logic.
"""

import os
import time
import requests
import json
from datetime import datetime
import logging
from typing import Dict, Optional, List
import threading
import signal
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('whatsapp_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WhatsAppAutomation:
    def __init__(self):
        # Load credentials from environment variables
        self.api_token = os.getenv('WHAPI_TOKEN')
        self.api_url_base = os.getenv('WHAPI_BASE_URL', 'https://gate.whapi.cloud')

        if not self.api_token or self.api_token == 'your_actual_whapi_cloud_token_here':
            raise ValueError("WHAPI_TOKEN environment variable is required and must be set to your actual whapi.cloud token")

        # AI-related keywords for detection
        self.ai_keywords = [
            'ai', 'artificial intelligence', 'chatgpt', 'llm', 'large language model',
            'automation', 'agents', 'python', 'javascript', 'ml', 'machine learning',
            'neural network', 'deep learning', 'nlp', 'natural language processing',
            'gpt', 'openai', 'anthropic', 'claude', 'ai assistant', 'bot',
            'programming', 'coding', 'software', 'development', 'algorithm',
            'data science', 'analytics', 'computer vision', 'robotics'
        ]

        # Headers for API requests
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_token}"
        }

        # Track processed messages to avoid duplicates
        self.processed_messages = set()

        # Server configuration
        self.webhook_port = int(os.getenv('WEBHOOK_PORT', 8000))
        self.polling_interval = int(os.getenv('POLLING_INTERVAL', 30))  # seconds

        logger.info("WhatsApp Automation system initialized")

    def is_ai_related(self, message_text: str) -> bool:
        """
        Check if the message is related to AI based on keywords
        """
        text_lower = message_text.lower()
        for keyword in self.ai_keywords:
            if keyword in text_lower:
                return True
        return False

    def generate_claude_reply(self, message_text: str) -> str:
        """
        Generate a reply using Claude Code integration
        This method should route the message to Claude Code for processing
        """
        logger.info(f"Routing AI-related message to Claude Code for response: {message_text[:100]}...")

        # In a real implementation, you would integrate with Claude Code here
        # For now, we'll simulate the Claude Code response generation
        # The actual implementation would involve calling Claude Code APIs

        # Simulate Claude Code processing
        import time
        time.sleep(1)  # Simulate processing time

        # Create a simulated Claude Code response
        ai_response_templates = [
            f"I noticed you mentioned something about AI in your message '{message_text[:50]}...'. "
            "AI is fascinating! Would you like to discuss more about artificial intelligence?",

            f"Thanks for your message about '{message_text[:50]}...'. "
            "As an AI system, I'm designed to help with AI-related inquiries. "
            "What specific aspect of AI interests you?",

            f"I see you're interested in AI topics like '{message_text[:50]}...'. "
            "Artificial intelligence is transforming many industries. "
            "What would you like to know more about?"
        ]

        # Heuristic-based response
        if 'python' in message_text.lower():
            response = ("Python is excellent for AI development! Popular libraries include "
                       "TensorFlow, PyTorch, scikit-learn, and pandas. Are you working on "
                       "an AI project with Python?")
        elif 'javascript' in message_text.lower():
            response = ("JavaScript is increasingly used in AI, especially for frontend "
                       "applications with TensorFlow.js. Are you exploring AI in web development?")
        elif any(word in message_text.lower() for word in ['chatgpt', 'gpt', 'openai']):
            response = ("ChatGPT is a great example of large language models! At Anthropic, "
                       "we focus on building safe and beneficial AI systems like Claude. "
                       "What would you like to know about AI safety and alignment?")
        else:
            import random
            response = random.choice(ai_response_templates)

        logger.info(f"Claude Code generated response: {response[:100]}...")
        return response

    def send_whatsapp_message(self, phone_number: str, message: str) -> bool:
        """
        Send a WhatsApp message using whapi.cloud API
        """
        try:
            url = f"{self.api_url_base}/messages/text"

            payload = {
                "typing_time": 0,
                "to": phone_number,
                "body": message
            }

            response = requests.post(url, json=payload, headers=self.headers)

            if response.status_code == 200:
                logger.info(f"Message sent successfully to {phone_number}")
                return True
            else:
                logger.error(f"Failed to send message: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error sending message to {phone_number}: {str(e)}")
            return False

    def get_recent_messages(self) -> List[Dict]:
        """
        Get recent messages from whapi.cloud
        Based on whapi.cloud API documentation for retrieving messages
        """
        try:
            # According to whapi.cloud documentation, the correct endpoint for messages is:
            # /messages with various query parameters
            url = f"{self.api_url_base}/messages"

            logger.info(f"Attempting to fetch messages from: {url}")

            # Parameters to get only incoming messages
            params = {
                'limit': 50,  # Get last 50 messages
                'direction': 'incoming',  # Only incoming messages
                'view': 'simple',  # Simple view to get basic message data
            }

            response = requests.get(url, headers=self.headers, params=params)

            logger.info(f"Endpoint {url} returned status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()

                # Log the response structure for debugging
                logger.debug(f"Response keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")

                # Handle different possible response structures
                messages = []
                if 'messages' in data:
                    messages = data['messages']
                    logger.info(f"Found 'messages' key with {len(messages)} items")
                elif 'data' in data and 'messages' in data['data']:
                    messages = data['data']['messages']
                    logger.info(f"Found 'data.messages' with {len(messages)} items")
                elif 'data' in data and isinstance(data['data'], list):
                    messages = data['data']
                    logger.info(f"Found 'data' as list with {len(messages)} items")
                elif isinstance(data, list):
                    # If response is directly an array of messages
                    messages = data
                    logger.info(f"Response is direct list with {len(messages)} items")
                else:
                    # Try to find message-like objects in the response
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if isinstance(value, list) and len(value) > 0 and key != 'status':
                                # Check if items in the list look like messages
                                if isinstance(value[0], dict) and any(field in value[0] for field in ['from', 'sender', 'contact', 'body', 'text', 'type']):
                                    messages = value
                                    logger.info(f"Found messages in '{key}' with {len(messages)} items")
                                    break
                    logger.debug(f"No standard message structure found in response")

                logger.info(f"Total messages found: {len(messages)}")

                if messages:
                    # Filter to only include text messages that haven't been processed
                    filtered_messages = []
                    for msg in messages:
                        # Extract message ID (try multiple possible fields)
                        msg_id = (msg.get('id') or
                                 msg.get('_id') or
                                 msg.get('messageId') or
                                 msg.get('message_id') or
                                 str(hash(str(msg)))[:16])  # Fallback to hash

                        # Determine if it's an incoming message
                        direction = str(msg.get('direction', '')).lower()
                        is_incoming = (direction == 'incoming' or
                                     msg.get('type') == 'text' and
                                     'from' in msg or  # Has a sender (incoming message)
                                     'sender' in msg or
                                     'contact' in msg)

                        # Determine if it's a text message
                        msg_type = msg.get('type', 'unknown')
                        is_text = (msg_type == 'text' or
                                  'body' in msg or
                                  'text' in msg or
                                  'content' in msg)

                        # Additional check: ensure it's actually a received message
                        # In whapi.cloud, received messages often have specific indicators
                        has_sender = bool(msg.get('from') or msg.get('sender') or msg.get('contact'))

                        # Check if not already processed
                        if is_incoming and is_text and has_sender and msg_id not in self.processed_messages:
                            # Add the ID to the message for tracking
                            msg['_internal_id'] = msg_id
                            filtered_messages.append(msg)

                    logger.info(f"Filtered to {len(filtered_messages)} new unprocessed incoming text messages")

                    if filtered_messages:
                        for msg in filtered_messages:
                            logger.debug(f"Found incoming message: ID={msg.get('_internal_id')}, From={msg.get('from', msg.get('sender', 'unknown'))}, Body={str(msg.get('body', msg.get('text', ''))[:50])}...")

                    return filtered_messages
                else:
                    logger.info("No messages found in response")
            elif response.status_code == 404:
                logger.warning(f"Messages endpoint not found (404). This may indicate that the account uses webhooks instead of polling.")
                logger.warning("Please check your whapi.cloud dashboard to see if webhooks are configured.")
            else:
                logger.warning(f"Endpoint returned status {response.status_code}: {response.text}")
                logger.warning("This could indicate an authentication issue or incorrect API usage.")

            # If the primary endpoint didn't work, try alternative approaches
            logger.info("Trying alternative approach - checking for any recent activity...")

            # Try to get conversations which might contain messages
            conversations_url = f"{self.api_url_base}/conversations"
            conv_response = requests.get(conversations_url, headers=self.headers)

            if conv_response.status_code == 200:
                conv_data = conv_response.json()
                logger.info(f"Conversations endpoint returned {conv_response.status_code}, checking for messages...")

                # Look for messages inside conversations
                if 'conversations' in conv_data:
                    for conv in conv_data['conversations']:
                        if 'messages' in conv:
                            logger.info(f"Found {len(conv['messages'])} messages in conversation")
                            # Process these messages similarly
                            for msg in conv['messages']:
                                msg_id = (msg.get('id') or
                                         str(hash(str(msg)))[:16])

                                direction = str(msg.get('direction', '')).lower()
                                is_incoming = (direction == 'incoming' or 'from' in msg)
                                is_text = (msg.get('type') == 'text' or 'body' in msg)
                                has_sender = bool(msg.get('from') or msg.get('sender'))

                                if is_incoming and is_text and has_sender and msg_id not in self.processed_messages:
                                    msg['_internal_id'] = msg_id
                                    filtered_messages.append(msg)

            return filtered_messages

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            logger.error("This could be due to network issues or incorrect API endpoint.")
        except Exception as e:
            logger.error(f"Unexpected error getting messages: {str(e)}", exc_info=True)

        logger.warning("Could not retrieve messages from any endpoint. This could indicate:")
        logger.warning("1. No new incoming messages are available")
        logger.warning("2. The account might be using webhooks instead of polling")
        logger.warning("3. The API response format is different than expected")
        logger.warning("4. There might be a configuration issue with your whapi.cloud account")
        return []

    def process_message(self, message_data: Dict):
        """
        Process an incoming message
        """
        try:
            # Extract message details according to whapi.cloud API response format
            message_id = message_data.get('id', message_data.get('_id', ''))

            # Extract sender (could be from, sender, or source depending on API response)
            sender = (message_data.get('from', {}) or
                     message_data.get('sender', {}) or
                     message_data.get('source', {}))

            # Handle different possible formats for sender
            if isinstance(sender, dict):
                phone_number = sender.get('phone', sender.get('wa_id', sender.get('id', '')))
            else:
                phone_number = str(sender) if sender else ''

            # Extract message text
            message_body = message_data.get('body', {})
            if isinstance(message_body, dict):
                message_text = message_body.get('text', message_body.get('body', ''))
            else:
                message_text = str(message_body) if message_body else ''

            # Alternative text extraction methods
            if not message_text:
                message_text = (message_data.get('text', {}).get('body', '') or
                               message_data.get('message', {}).get('text', '') or
                               message_data.get('content', '') or
                               '')

            if not message_text:
                logger.debug(f"Skipping message {message_id} - no text content")
                return  # Skip if no text content

            # Normalize phone number format (remove any prefixes if needed)
            if phone_number and phone_number.startswith('tel:'):
                phone_number = phone_number[4:]

            # Remove non-digit characters except +
            import re
            phone_number = re.sub(r'[^\d+]', '', phone_number)

            # Check if already processed
            if message_id in self.processed_messages:
                logger.debug(f"Message {message_id} already processed, skipping")
                return

            self.processed_messages.add(message_id)

            logger.info(f"Incoming message from {phone_number}: {message_text}")

            # Check if AI-related
            logger.info(f"Checking if message is AI-related...")
            is_ai_related_result = self.is_ai_related(message_text)
            logger.info(f"AI-detection result: {is_ai_related_result}")

            if is_ai_related_result:
                logger.info(f"AI-related message detected from {phone_number}")

                # Generate Claude Code reply
                reply = self.generate_claude_reply(message_text)
                logger.info(f"Claude Code response generated: {reply[:100]}...")

                # Send the reply back to WhatsApp
                logger.info(f"Sending reply to {phone_number}: {reply[:100]}...")
                success = self.send_whatsapp_message(phone_number, reply)

                if success:
                    logger.info(f"Reply successfully sent to {phone_number}")
                else:
                    logger.error(f"Failed to send reply to {phone_number}")
            else:
                logger.info(f"Non-AI message from {phone_number}, skipping...")

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)

    def start_polling(self):
        """
        Start polling for new messages
        """
        logger.info("Starting message polling...")

        def polling_loop():
            while True:
                try:
                    # Get recent messages
                    messages = self.get_recent_messages()

                    # Process each message
                    for message in messages:
                        self.process_message(message)

                    # Wait before next poll
                    time.sleep(self.polling_interval)

                except KeyboardInterrupt:
                    logger.info("Polling interrupted by user")
                    break
                except Exception as e:
                    logger.error(f"Error in polling loop: {str(e)}")
                    time.sleep(self.polling_interval)

        # Start polling in a separate thread
        polling_thread = threading.Thread(target=polling_loop, daemon=True)
        polling_thread.start()

        return polling_thread

    def start_webhook_server(self):
        """
        Start a webhook server to receive messages
        """
        class MessageHandler(BaseHTTPRequestHandler):
            def do_POST(self):
                try:
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)

                    # Parse the message data
                    message_data = json.loads(post_data.decode('utf-8'))

                    # Process the message
                    whatsapp_auto.process_message(message_data)

                    # Send response
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "success"}).encode())

                except Exception as e:
                    logger.error(f"Error processing webhook: {str(e)}")
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode())

            def log_message(self, format, *args):
                logger.info(f"Webhook request: {format % args}")

        server = HTTPServer(('', self.webhook_port), MessageHandler)
        logger.info(f"Starting webhook server on port {self.webhook_port}")

        def server_loop():
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                logger.info("Webhook server interrupted by user")
            finally:
                server.shutdown()

        # Start server in a separate thread
        server_thread = threading.Thread(target=server_loop, daemon=True)
        server_thread.start()

        return server_thread, server

    def start(self, use_webhook=False):
        """
        Start the WhatsApp automation system
        """
        logger.info("Starting WhatsApp Automation System...")

        threads = []

        if use_webhook:
            # Start webhook server
            server_thread, server = self.start_webhook_server()
            threads.append(server_thread)
        else:
            # Start polling
            polling_thread = self.start_polling()
            threads.append(polling_thread)

        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down WhatsApp Automation System...")
            if 'server' in locals():
                server.shutdown()


def manual_send_message(phone_number: str, message: str):
    """
    Manually send a WhatsApp message to any number
    """
    whatsapp_auto = WhatsAppAutomation()
    return whatsapp_auto.send_whatsapp_message(phone_number, message)


def main():
    """
    Main entry point
    """
    # Check if running in webhook mode
    use_webhook = os.getenv('USE_WEBHOOK', 'false').lower() == 'true'

    whatsapp_auto = WhatsAppAutomation()
    whatsapp_auto.start(use_webhook=use_webhook)


if __name__ == "__main__":
    main()