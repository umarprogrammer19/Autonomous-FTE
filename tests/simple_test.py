#!/usr/bin/env python3
"""
Simple test to verify all components work correctly
"""

def test_email_service():
    """Test the email service"""
    print("Testing email service...")

    from services.email_service import EmailService
    result = EmailService.send_email(
        "test@example.com",
        "Test Subject from Service",
        "Test message from service layer"
    )
    print(f"Email service result: {result}")
    return result

def test_whatsapp_service():
    """Test the WhatsApp service"""
    print("Testing WhatsApp service...")

    from services.whatsapp_service import WhatsAppService
    result = WhatsAppService.send_message(
        "923182710120",
        "Test message from service layer"
    )
    print(f"WhatsApp service result: {result}")
    return result

def test_ai_post_service():
    """Test the AI post service"""
    print("Testing AI post service...")

    from services.ai_post_service import AIPostService
    result = AIPostService.generate_and_post_now()
    print(f"AI post service result: {result}")
    return result

if __name__ == "__main__":
    print("Running service tests...\n")

    try:
        email_ok = test_email_service()
        whatsapp_ok = test_whatsapp_service()
        ai_ok = test_ai_post_service()

        print(f"\nResults:")
        print(f"Email service: {'PASS' if email_ok else 'FAIL'}")
        print(f"WhatsApp service: {'PASS' if whatsapp_ok else 'FAIL'}")
        print(f"AI post service: {'PASS' if ai_ok else 'FAIL'}")

        if all([email_ok, whatsapp_ok, ai_ok]):
            print("\nAll services working correctly!")
        else:
            print("\nSome services had issues.")

    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()