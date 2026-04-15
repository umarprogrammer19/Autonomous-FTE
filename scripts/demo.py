"""
Demo script for WhatsApp Automation System
Shows how to use the various features
"""

import os
from whatsapp_automation import WhatsAppAutomation, manual_send_message
from utils import load_env


def demo_keyword_detection():
    """Demonstrate AI keyword detection"""
    print("=== AI Keyword Detection Demo ===")

    # Mock environment for demo
    os.environ['WHAPI_TOKEN'] = 'demo_token'
    wa = WhatsAppAutomation()

    test_messages = [
        "I'm learning Python for AI development",
        "What do you think about ChatGPT?",
        "Machine learning is fascinating!",
        "How's the weather today?",
        "I need help with my LLM project in JavaScript"
    ]

    for msg in test_messages:
        is_ai = wa.is_ai_related(msg)
        print(f"Message: '{msg}' -> AI-related: {is_ai}")

    print()


def demo_reply_generation():
    """Demonstrate reply generation"""
    print("=== Reply Generation Demo ===")

    os.environ['WHAPI_TOKEN'] = 'demo_token'
    wa = WhatsAppAutomation()

    test_messages = [
        "I'm learning Python for AI",
        "What do you think about ChatGPT?",
        "Tell me about machine learning"
    ]

    for msg in test_messages:
        reply = wa.generate_claude_reply(msg)
        print(f"Input: '{msg}'")
        print(f"Reply: '{reply}'")
        print()

    print()


def demo_manual_sending():
    """Demonstrate manual message sending (will fail without real token)"""
    print("=== Manual Message Sending Demo ===")
    print("Note: This would require a real whapi.cloud token to work")

    # This is just to show the function exists
    # It will fail without a real token
    try:
        success = manual_send_message("923182710120", "Hello from demo!")
        print(f"Sending message to 923182710120: {'Success' if success else 'Failed'}")
    except Exception as e:
        print(f"Expected failure in demo mode: {e}")

    print()


def main():
    print("WhatsApp Automation System Demo")
    print("=" * 40)

    demo_keyword_detection()
    demo_reply_generation()
    demo_manual_sending()

    print("For full functionality:")
    print("1. Set your WHAPI_TOKEN in .env file")
    print("2. Run: python whatsapp_automation.py")
    print("3. Or use CLI: python whatsapp_cli.py start")


if __name__ == "__main__":
    main()