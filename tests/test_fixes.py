#!/usr/bin/env python3
"""
Test script to verify all components work correctly
"""

import subprocess
import sys
import os
import json

def test_email_script():
    """Test the email script with dynamic parameters"""
    print("Testing email script...")

    # Test with sample parameters
    cmd = [
        sys.executable,
        "email_mcp_server.py",
        "test@example.com",
        "Test Subject from Streamlit",
        "Test message from Streamlit UI"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        print(f"Email script return code: {result.returncode}")
        print(f"Email script stdout: {result.stdout}")
        print(f"Email script stderr: {result.stderr}")

        if result.returncode == 0:
            print("✅ Email script test PASSED")
            return True
        else:
            print("❌ Email script test FAILED")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Email script test TIMED OUT")
        return False
    except Exception as e:
        print(f"❌ Email script test ERROR: {e}")
        return False

def test_whatsapp_script():
    """Test the WhatsApp script"""
    print("\nTesting WhatsApp script...")

    cmd = [
        sys.executable,
        "whatsapp_sender.py",
        "923182710120",  # Test phone number
        "Test message from Streamlit UI"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        print(f"WhatsApp script return code: {result.returncode}")
        print(f"WhatsApp script stdout: {result.stdout}")
        print(f"WhatsApp script stderr: {result.stderr}")

        if result.returncode == 0:
            print("✅ WhatsApp script test PASSED")
            return True
        else:
            print("❌ WhatsApp script test FAILED")
            return False
    except subprocess.TimeoutExpired:
        print("❌ WhatsApp script test TIMED OUT")
        return False
    except Exception as e:
        print(f"❌ WhatsApp script test ERROR: {e}")
        return False

def test_ai_scheduler_manual():
    """Test the AI scheduler in manual mode"""
    print("\nTesting AI scheduler (manual mode)...")

    cmd = [
        sys.executable,
        "daily_ai_scheduler.py",
        "--manual"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        print(f"AI scheduler return code: {result.returncode}")
        print(f"AI scheduler stdout: {result.stdout}")
        print(f"AI scheduler stderr: {result.stderr}")

        if result.returncode == 0:
            print("✅ AI scheduler manual test PASSED")
            return True
        else:
            print("❌ AI scheduler manual test FAILED")
            return False
    except subprocess.TimeoutExpired:
        print("❌ AI scheduler manual test TIMED OUT")
        return False
    except Exception as e:
        print(f"❌ AI scheduler manual test ERROR: {e}")
        return False

def test_services_integration():
    """Test the service layer integration"""
    print("\nTesting service layer integration...")

    try:
        # Test email service
        from services.email_service import EmailService
        email_result = EmailService.send_email(
            "test@example.com",
            "Test from Service Layer",
            "Test message from service layer"
        )
        print(f"Email service result: {email_result}")

        # Test WhatsApp service
        from services.whatsapp_service import WhatsAppService
        whatsapp_result = WhatsAppService.send_message(
            "923182710120",
            "Test from Service Layer"
        )
        print(f"WhatsApp service result: {whatsapp_result}")

        # Test AI post service
        from services.ai_post_service import AIPostService
        ai_result = AIPostService.generate_and_post_now()
        print(f"AI post service result: {ai_result}")

        # Check if latest post was created
        if os.path.exists('data/latest_post.json'):
            with open('data/latest_post.json', 'r') as f:
                latest_post = json.load(f)
            print(f"Latest post content: {latest_post.get('content', 'N/A')}")

        print("✅ Service layer integration test completed")
        return True

    except Exception as e:
        print(f"❌ Service layer integration test ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running comprehensive tests...\n")

    results = []
    results.append(test_email_script())
    results.append(test_whatsapp_script())
    results.append(test_ai_scheduler_manual())
    results.append(test_services_integration())

    print(f"\nTest Results: {sum(results)}/{len(results)} passed")

    if all(results):
        print("🎉 All tests PASSED!")
    else:
        print("⚠️ Some tests FAILED!")
        sys.exit(1)