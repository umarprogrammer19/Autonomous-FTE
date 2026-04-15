"""
Test script for WhatsApp Sender functionality
"""

from whatsapp_sender_demo import WhatsAppSender

def test_sender():
    """Test the WhatsApp sender functionality"""
    print("Testing WhatsApp Sender Functionality")
    print("=" * 40)

    try:
        # Create sender with test token
        sender = WhatsAppSender(use_test_token=True)

        print("[SUCCESS] WhatsAppSender initialized successfully")
        print(f"[INFO] Available contacts: {list(sender.contacts.keys())}")

        # Test contact matching
        test_contacts = ['ahsen', 'adil', 'unknown']
        for contact in test_contacts:
            number = sender.match_contact(contact)
            if number:
                print(f"[FOUND] '{contact}' -> {number}")
            else:
                print(f"[MISSING] '{contact}' -> Not found")

        # Test sending a message (this will fail due to invalid token but will show the process)
        print("\nTesting message sending process...")
        result = sender.send_message_to_contact('ahsen', 'Hello from test!')
        print(f"Message sending result: {result}")

    except Exception as e:
        print(f"[ERROR] Error during testing: {e}")

if __name__ == "__main__":
    test_sender()