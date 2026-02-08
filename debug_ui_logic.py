import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from services.ai_post_service import AIPostService

def test_manual_button_logic():
    """Simulate the exact logic used in the manual button"""
    print("Testing manual button logic...")

    try:
        # Generate and post immediately (same as UI)
        result = AIPostService.generate_and_post_now()
        if result:
            print("SUCCESS: AI post generated and published successfully!")
            print(f"Updated total posts: +1")
            print(f"Updated last post time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("FAILURE: Failed to generate and post.")
    except Exception as e:
        print(f"EXCEPTION: Error generating post: {str(e)}")

if __name__ == "__main__":
    test_manual_button_logic()