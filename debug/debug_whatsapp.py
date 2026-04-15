"""
Debug script to test WhatsApp automation functionality
"""

import os
from unittest.mock import patch, MagicMock
from src.whatsapp_automation import WhatsAppAutomation

def test_message_processing():
    """Test the message processing pipeline"""
    print("Testing WhatsApp message processing...")

    # Set up environment
    os.environ['WHAPI_TOKEN'] = 'test_token'

    # Create WhatsAppAutomation instance
    wa = WhatsAppAutomation()

    # Test message data in various possible whapi.cloud formats
    test_messages = [
        # Format 1: Standard message object
        {
            "id": "msg_123",
            "from": {
                "phone": "+1234567890"
            },
            "type": "text",
            "body": {
                "text": "I'm learning about Python and AI"
            },
            "direction": "incoming"
        },

        # Format 2: Different field names
        {
            "_id": "msg_124",
            "sender": {
                "wa_id": "+1987654321"
            },
            "type": "text",
            "text": {
                "body": "What do you think about ChatGPT?"
            },
            "direction": "incoming"
        },

        # Format 3: Direct fields
        {
            "id": "msg_125",
            "from": "+1122334455",
            "type": "text",
            "body": "Machine learning is amazing!",
            "direction": "incoming"
        },

        # Format 4: Non-AI message to test filtering
        {
            "id": "msg_126",
            "from": "+1555666777",
            "type": "text",
            "body": "What's for dinner tonight?",
            "direction": "incoming"
        }
    ]

    print("\n--- Testing message processing ---")
    for i, msg in enumerate(test_messages):
        body_text = msg.get('body', {})
        if isinstance(body_text, str):
            display_text = body_text
        elif isinstance(body_text, dict):
            display_text = body_text.get('text', body_text.get('body', 'Unknown'))
        else:
            display_text = str(body_text)

        print(f"\nTest {i+1}: {display_text}")

        # Process the message
        wa.process_message(msg)

    print("\n--- Testing AI keyword detection ---")
    test_texts = [
        "I'm learning about Python and AI",
        "What do you think about ChatGPT?",
        "Machine learning is amazing!",
        "What's for dinner tonight?",
        "JavaScript for AI applications"
    ]

    for text in test_texts:
        is_ai = wa.is_ai_related(text)
        print(f"'{text}' -> AI-related: {is_ai}")

    print("\n--- Testing Claude Code response generation ---")
    ai_texts = [
        "I'm learning about Python and AI",
        "What do you think about ChatGPT?",
        "Tell me about machine learning"
    ]

    for text in ai_texts:
        response = wa.generate_claude_reply(text)
        print(f"Input: '{text}'")
        print(f"Response: '{response[:100]}...'")
        print()

def test_api_calls():
    """Test the API call functionality"""
    print("Testing API call functionality...")

    os.environ['WHAPI_TOKEN'] = 'test_token'
    wa = WhatsAppAutomation()

    # Mock the requests.get call to simulate whapi.cloud API response
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "messages": [
                {
                    "id": "msg_127",
                    "from": {"phone": "+1234567890"},
                    "type": "text",
                    "body": "I love artificial intelligence!",
                    "direction": "incoming"
                }
            ]
        }
        mock_get.return_value = mock_response

        messages = wa.get_recent_messages()
        print(f"Retrieved {len(messages)} messages from API mock")
        if messages:
            print(f"First message: {messages[0]['body']}")

if __name__ == "__main__":
    print("WhatsApp Automation Debug Script")
    print("=" * 40)

    test_message_processing()
    print("\n" + "=" * 40)
    test_api_calls()

    print("\nDebug complete!")