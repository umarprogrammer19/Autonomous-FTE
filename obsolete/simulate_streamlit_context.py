"""
Simulate the exact context that Streamlit creates when the button is clicked.
"""
import subprocess
import sys
import threading
import time
from src.services.ai_post_service import AIPostService

def simulate_ui_call():
    """Simulate calling the AI post service as Streamlit would"""
    print("Simulating UI context call...")

    # This mimics what happens when the button is clicked in Streamlit
    try:
        result = AIPostService.generate_and_post_now()
        print(f"Result from AIPostService: {result}")

        if result:
            print("SUCCESS: AI post generated and published!")
            # Simulate updating session state as UI would
            print("Updating simulated session state...")
        else:
            print("FAILURE: AI post generation failed!")

    except Exception as e:
        print(f"EXCEPTION in simulated UI call: {str(e)}")
        import traceback
        traceback.print_exc()

def simulate_with_timeout():
    """Test with potential timeout scenarios"""
    print("\nTesting with timeout constraints...")

    def run_service():
        return AIPostService.generate_and_post_now()

    # Create a thread to run the service call
    result_container = [None]
    exception_container = [None]

    def target():
        try:
            result_container[0] = AIPostService.generate_and_post_now()
        except Exception as e:
            exception_container[0] = e

    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()

    # Wait for completion (similar to how Streamlit might handle it)
    thread.join(timeout=10)  # 10 second timeout

    if thread.is_alive():
        print("WARNING: Thread is still alive - potential timeout issue")
        return False
    elif exception_container[0]:
        print(f"EXCEPTION caught: {exception_container[0]}")
        return False
    else:
        print(f"Thread completed with result: {result_container[0]}")
        return result_container[0]

if __name__ == "__main__":
    print("Testing simulated Streamlit context...")
    simulate_ui_call()

    print("\n" + "="*50)
    simulate_with_timeout()