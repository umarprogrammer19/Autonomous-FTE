import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta
import os
import json
from typing import Dict, Optional

class AIPostService:
    """Service class to handle AI post generation and scheduling"""

    @staticmethod
    def generate_and_post_now() -> bool:
        """
        Generate and post an AI-generated post immediately

        Returns:
            bool: True if post generated and posted successfully, False otherwise
        """
        try:
            # Call the daily_ai_scheduler with --test flag to run once
            cmd = [sys.executable, "daily_ai_scheduler.py", "--test"]

            # Run the scheduler for one iteration only
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # Longer timeout for AI generation
            )

            if result.returncode == 0:
                print("AI post generated and posted successfully")
                return True
            else:
                print(f"Error generating post: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("Error: AI post generation timed out")
            return False
        except FileNotFoundError:
            print("Error: daily_ai_scheduler.py not found")
            return False
        except Exception as e:
            print(f"Unexpected error generating post: {str(e)}")
            return False

    @staticmethod
    def get_latest_post() -> Optional[Dict]:
        """
        Get the latest generated post info

        Returns:
            Dict: Post information or None if not available
        """
        try:
            if os.path.exists('data/latest_post.json'):
                with open('data/latest_post.json', 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"Error reading latest post: {str(e)}")
            return None

    @staticmethod
    def run_scheduler_background():
        """
        Run the daily AI scheduler in the background
        This method should be called in a separate thread
        """
        try:
            # Remove any existing lock file to ensure clean start
            lock_file = 'data/scheduler.lock'
            if os.path.exists(lock_file):
                os.remove(lock_file)

            print("Starting AI scheduler...")

            # The actual scheduler runs continuously, but we need to respect Streamlit's session state
            # Since the scheduler runs forever, we'll just start it and let it run
            # The lock file mechanism will prevent multiple instances
            cmd = [sys.executable, "daily_ai_scheduler.py"]

            # Run the scheduler - it handles its own timing
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=None  # No timeout - this will run continuously
            )

            if result.returncode == 0:
                print("AI scheduler completed successfully")
            else:
                print(f"AI scheduler failed: {result.stderr}")

        except Exception as e:
            print(f"Error in scheduler: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            # Clean up lock file when scheduler stops
            lock_file = 'data/scheduler.lock'
            if os.path.exists(lock_file):
                os.remove(lock_file)

    @staticmethod
    def stop_scheduler():
        """
        Stop the running scheduler
        """
        try:
            import streamlit as st
            st.session_state.scheduler_running = False
            print("Scheduler stopped")
        except Exception as e:
            print(f"Error stopping scheduler: {str(e)}")