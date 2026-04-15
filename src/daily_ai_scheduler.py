"""
Daily AI Post Scheduler

This script runs every 24 hours to:
1. Trigger automatically
2. Hand over control to Claude Code (ccr code)
3. Have Claude Code search for trending AI topics and generate a post
4. Save the post in markdown format
"""

import os
import time
import schedule
import logging
from datetime import datetime
import subprocess
import sys
from pathlib import Path


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_ai_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DailyAIPostScheduler:
    def __init__(self, posts_directory="Daily_AI_Posts"):
        self.posts_directory = Path(posts_directory)

        # Create the posts directory if it doesn't exist
        self.posts_directory.mkdir(exist_ok=True)

        logger.info(f"Daily AI Post Scheduler initialized")
        logger.info(f"Posts will be saved to: {self.posts_directory.absolute()}")

    def generate_ai_post(self):
        """
        Generate an AI post by logically handing over control to Claude Code
        """
        logger.info("Logically handing over control to Claude Code (ccr code) for AI post generation")

        # Get today's date for the filename
        today_date = datetime.now().strftime("%Y-%m-%d")
        filename = f"{today_date}_ai_trending_post.md"
        filepath = self.posts_directory / filename

        # Simulate the logical handoff to Claude Code
        # In a real scenario, this would be where Claude Code takes over internally
        logger.info(f"Simulating Claude Code handoff: ccr code - search trending AI topics and generate post")

        # For simulation purposes, we'll create a sample AI post
        # In the real scenario, Claude Code would handle this internally

        trending_topic = self.select_trending_ai_topic()
        ai_post_content = self.generate_sample_ai_post(trending_topic)

        try:
            # Write the AI post to the markdown file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(ai_post_content)

            logger.info(f"Successfully generated AI post: {filename}")
            logger.info(f"Post file created successfully: {filepath}")

            # Log file size
            file_size = filepath.stat().st_size
            logger.info(f"Post file size: {file_size} bytes")

            # After creating the post, trigger social posting
            self.trigger_social_post(filepath)

            return True

        except Exception as e:
            logger.error(f"Error creating AI post file: {str(e)}")
            return False

    def trigger_social_post(self, filepath):
        """
        Trigger social media posting for the newly created file
        """
        try:
            from social_poster import SocialPoster

            # Create a SocialPoster instance and post the content
            poster = SocialPoster()

            # Extract title and body from the file
            title, caption = poster.extract_title_and_body(filepath)

            if title and caption:
                # Post to social media
                success, response = poster.post_to_social_media(title, caption)

                if success:
                    logger.info(f"Successfully posted {filepath.name} to social media")

                    # Create a marker file to indicate this file has been posted
                    posted_marker = filepath.with_suffix('.posted')
                    posted_marker.touch()
                else:
                    logger.error(f"Failed to post {filepath.name} to social media: {response}")
            else:
                logger.warning(f"Could not extract content from {filepath.name}, skipping social post")

        except ImportError:
            logger.warning(f"Social poster module not available, skipping social posting for {filepath.name}")
        except Exception as e:
            logger.error(f"Error triggering social post for {filepath.name}: {str(e)}")

    def select_trending_ai_topic(self):
        """
        Select a trending AI topic (in a real scenario, Claude Code would do this)
        """
        import random
        trending_topics = [
            "Generative AI in Healthcare",
            "Large Language Model Optimization",
            "AI Ethics and Responsible Development",
            "Multimodal AI Systems",
            "AI-Powered Automation Trends",
            "Foundation Models Evolution",
            "AI in Scientific Discovery",
            "Neural Network Architecture Innovations",
            "AI Safety and Alignment Research",
            "Enterprise AI Adoption Strategies"
        ]

        selected_topic = random.choice(trending_topics)
        logger.info(f"Selected trending AI topic: {selected_topic}")
        return selected_topic

    def generate_sample_ai_post(self, topic):
        """
        Generate a sample AI post (in a real scenario, Claude Code would do this)
        """
        from datetime import datetime

        content = f"""# {topic}: Latest Developments and Industry Impact

## Introduction

{topic} represents one of the most significant trends in artificial intelligence today. This comprehensive overview explores the current state, practical applications, and future implications of this rapidly evolving field.

## Current State of {topic}

The landscape of {topic} has experienced remarkable growth in recent months, with breakthrough developments occurring at an unprecedented pace. Industry leaders and researchers are pushing the boundaries of what's possible, creating new opportunities and challenges simultaneously.

## Practical Applications

Real-world implementations of {topic} are already transforming various sectors:

- **Healthcare**: Revolutionizing diagnosis and treatment protocols
- **Finance**: Enhancing risk assessment and fraud detection
- **Education**: Personalizing learning experiences at scale
- **Manufacturing**: Optimizing supply chains and production workflows

## Industry Relevance

Organizations across industries are recognizing the strategic importance of {topic} in maintaining competitive advantage. Early adopters are already seeing significant benefits in efficiency, accuracy, and innovation capacity.

## Future Outlook

The trajectory for {topic} indicates continued rapid advancement, with emerging trends pointing toward:

- Increased integration with existing systems
- Enhanced accessibility for smaller organizations
- Improved ethical frameworks and governance
- Cross-disciplinary collaboration opportunities

## Conclusion

{topic} continues to shape the future of artificial intelligence, offering substantial opportunities for those positioned to leverage its potential effectively.

---

*Published on {datetime.now().strftime('%Y-%m-%d')}*
*Generated by Daily AI Post Scheduler*
"""
        return content

    def scheduled_task(self):
        """
        The task that runs every 24 hours
        """
        logger.info("Scheduled task triggered - Starting daily AI post generation")

        # Record start time
        start_time = datetime.now()
        logger.info(f"Task started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Generate the AI post
        success = self.generate_ai_post()

        # Record end time
        end_time = datetime.now()
        duration = end_time - start_time

        logger.info(f"Task completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Task duration: {duration}")

        if success:
            logger.info("[SUCCESS] Daily AI post generation completed successfully")
        else:
            logger.error("[ERROR] Daily AI post generation failed")

        return success

    def start_scheduler(self):
        """
        Start the 24-hour scheduler
        """
        logger.info("Starting 24-hour AI post scheduler")
        logger.info("Scheduler will run every 24 hours")

        # Schedule the task to run every 24 hours
        schedule.every(24).hours.do(self.scheduled_task)

        # Also run it immediately for the first time
        logger.info("Running initial task...")
        self.scheduled_task()

        logger.info("Scheduler started successfully. Waiting for next scheduled run...")

        # Keep the scheduler running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def run_once_now(self):
        """
        Run the scheduled task once immediately (for testing)
        """
        logger.info("Running scheduled task once (on-demand)")
        return self.scheduled_task()


def main():
    """
    Main function to start the scheduler
    """
    print("Daily AI Post Scheduler")
    print("=" * 30)

    # Create the scheduler instance
    scheduler = DailyAIPostScheduler()

    # Check if running in test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Running in test mode (once)...")
        scheduler.run_once_now()
        print("Test completed.")
    else:
        print("Starting 24-hour scheduler...")
        print("Press Ctrl+C to stop the scheduler")

        try:
            scheduler.start_scheduler()
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            print("\nScheduler stopped by user")


if __name__ == "__main__":
    main()