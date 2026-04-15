"""
Minimal test to replicate the Streamlit UI logic for the manual button
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from services.ai_post_service import AIPostService

def simulate_manual_button_click():
    """
    Simulate exactly what happens when the manual button is clicked in Streamlit
    """
    print("Simulating manual button click logic...")

    try:
        # This is the exact same call as in the UI
        result = AIPostService.generate_and_post_now()

        print(f"Service result: {result}")

        if result:
            # This is what happens on success in the UI
            print("SUCCESS: AI post generated and published successfully!")

            # Simulate updating session state (as UI would)
            total_posts = 0  # This would come from session state
            last_post_time = None  # This would come from session state

            total_posts += 1
            last_post_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            print(f"Updated total posts: {total_posts}")
            print(f"Updated last post time: {last_post_time}")

        else:
            # This is the error that would be shown in UI
            print("ERROR: Failed to generate and post. Please check the logs.")

    except Exception as e:
        # This is the exception handling from the UI
        print(f"EXCEPTION: Error generating post: {str(e)}")

if __name__ == "__main__":
    simulate_manual_button_click()