"""
Combined Daily AI Scheduler with Social Posting

This script combines:
1. Daily AI post generation (every 24 hours)
2. Automatic social media posting when new posts are created
"""

import os
import time
import schedule
import logging
from datetime import datetime
from pathlib import Path
import threading
from daily_ai_scheduler import DailyAIPostScheduler
from social_poster import SocialPoster


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('combined_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CombinedScheduler:
    def __init__(self, posts_directory="Daily_AI_Posts", image_path="mug.png"):
        self.posts_directory = Path(posts_directory)
        self.image_path = Path(image_path)

        # Create the posts directory if it doesn't exist
        self.posts_directory.mkdir(exist_ok=True)

        # Initialize the AI post scheduler
        self.ai_scheduler = DailyAIPostScheduler(posts_directory=posts_directory)

        # Initialize the social poster
        self.social_poster = SocialPoster(posts_directory=posts_directory, image_path=image_path)

        logger.info("Combined Scheduler initialized")
        logger.info(f"Posts directory: {self.posts_directory.absolute()}")
        logger.info(f"Image path: {self.image_path}")

    def start_ai_scheduler(self):
        """
        Start the AI post generation scheduler
        """
        logger.info("Starting AI post generation scheduler (every 24 hours)")

        # Schedule the AI post generation every 24 hours
        schedule.every(24).hours.do(self.ai_scheduler.scheduled_task)

        # Run the first task immediately
        logger.info("Running initial AI post generation task...")
        self.ai_scheduler.scheduled_task()

        # Keep the scheduler running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def start_social_monitoring(self):
        """
        Start monitoring for new files to post to social media
        """
        logger.info("Starting social media posting monitor")

        # Process any existing files first
        self.social_poster.process_new_files()

        # Start monitoring for new files
        self.social_poster.start_monitoring(check_interval=30)  # Check every 30 seconds

    def start_both_services(self):
        """
        Start both the AI scheduler and social media monitor
        """
        logger.info("Starting both AI scheduler and social media services...")

        # Start the social media monitoring in a separate thread
        social_thread = threading.Thread(target=self.start_social_monitoring, daemon=True)
        social_thread.start()

        logger.info("Social media monitoring started in background thread")

        # Start the AI scheduler in the main thread
        logger.info("Starting AI post scheduler...")
        self.start_ai_scheduler()


def main():
    """
    Main function to run the combined scheduler
    """
    print("Combined Daily AI Scheduler with Social Posting")
    print("=" * 50)

    # Create the combined scheduler
    scheduler = CombinedScheduler()

    print(f"AI Posts Directory: {scheduler.posts_directory.absolute()}")
    print(f"Image File: {scheduler.image_path}")
    print()

    print("Starting services...")
    print("- AI Post Generation: Every 24 hours")
    print("- Social Media Posting: When new posts are created")
    print()
    print("Press Ctrl+C to stop all services")
    print()

    try:
        scheduler.start_both_services()
    except KeyboardInterrupt:
        logger.info("Services stopped by user")
        print("\nServices stopped by user")


if __name__ == "__main__":
    main()