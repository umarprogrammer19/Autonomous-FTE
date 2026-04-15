"""
Test script for WhatsApp Automation System
"""

import os
import sys
from unittest.mock import patch, MagicMock
import pytest

# Add current directory to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.whatsapp_automation import WhatsAppAutomation


def test_initialization():
    """Test initialization of WhatsAppAutomation class"""
    with patch.dict(os.environ, {"WHAPI_TOKEN": "test_token"}):
        wa = WhatsAppAutomation()

        assert wa.api_token == "test_token"
        assert "Bearer test_token" in wa.headers["authorization"]
        assert len(wa.ai_keywords) > 0


def test_is_ai_related():
    """Test AI keyword detection"""
    with patch.dict(os.environ, {"WHAPI_TOKEN": "test_token"}):
        wa = WhatsAppAutomation()

        # Test positive cases
        assert wa.is_ai_related("I love AI and machine learning")
        assert wa.is_ai_related("What do you think about ChatGPT?")
        assert wa.is_ai_related("Python is great for ML")
        assert wa.is_ai_related("Tell me about large language models")

        # Test negative cases
        assert not wa.is_ai_related("Hi, how are you?")
        assert not wa.is_ai_related("What's for dinner?")
        assert not wa.is_ai_related("The weather is nice today")


def test_generate_claude_reply():
    """Test Claude-like reply generation"""
    with patch.dict(os.environ, {"WHAPI_TOKEN": "test_token"}):
        wa = WhatsAppAutomation()

        reply = wa.generate_claude_reply("I'm learning about Python and AI")
        assert isinstance(reply, str)
        assert len(reply) > 0


@patch("requests.post")
def test_send_whatsapp_message(mock_post):
    """Test sending WhatsApp message"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '{"success": true}'
    mock_post.return_value = mock_response

    with patch.dict(os.environ, {"WHAPI_TOKEN": "test_token"}):
        wa = WhatsAppAutomation()

        result = wa.send_whatsapp_message("1234567890", "Hello")

        assert result is True
        mock_post.assert_called_once()


@patch("requests.post")
def test_send_whatsapp_message_failure(mock_post):
    """Test sending WhatsApp message failure"""
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = '{"error": "Invalid token"}'
    mock_post.return_value = mock_response

    with patch.dict(os.environ, {"WHAPI_TOKEN": "test_token"}):
        wa = WhatsAppAutomation()

        result = wa.send_whatsapp_message("1234567890", "Hello")

        assert result is False


def test_manual_send_message():
    """Test manual message sending function"""
    from src.whatsapp_automation import manual_send_message

    with patch.dict(os.environ, {"WHAPI_TOKEN": "test_token"}):
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = '{"success": true}'
            mock_post.return_value = mock_response

            result = manual_send_message("1234567890", "Test message")

            assert result is True


if __name__ == "__main__":
    print("Running tests for WhatsApp Automation System...")

    test_initialization()
    print("PASS: Initialization test passed")

    test_is_ai_related()
    print("PASS: AI keyword detection test passed")

    test_generate_claude_reply()
    print("PASS: Reply generation test passed")

    test_send_whatsapp_message()
    print("PASS: Message sending test passed")

    test_send_whatsapp_message_failure()
    print("PASS: Message sending failure test passed")

    test_manual_send_message()
    print("PASS: Manual send test passed")

    print("\nAll tests passed!")
