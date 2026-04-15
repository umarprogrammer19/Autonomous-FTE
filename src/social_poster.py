"""
Social Poster Module
Automatically posts content from Daily_AI_Posts/ to social media platforms
"""

import os
import time
import logging
from pathlib import Path
from datetime import datetime
import re
import markdown
from bs4 import BeautifulSoup


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('social_poster.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SocialPoster:
    def __init__(self, posts_directory="Daily_AI_Posts", image_path="ai.png"):
        self.posts_directory = Path(posts_directory)
        self.image_path = Path(image_path)

        # Create posts directory if it doesn't exist
        self.posts_directory.mkdir(exist_ok=True)

        logger.info(f"Social Poster initialized")
        logger.info(f"Monitoring directory: {self.posts_directory.absolute()}")
        logger.info(f"Using image: {self.image_path}")

    def extract_title_and_body(self, markdown_file_path):
        """
        Extract title and body from a markdown file
        """
        try:
            with open(markdown_file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract title (first H1 header)
            lines = content.split('\n')
            title = ""
            for line in lines:
                if line.strip().startswith('# ') or line.strip().startswith('## '):
                    title = line.strip('# ').strip()
                    break

            if not title:
                # If no H1 found, use first non-empty line as title
                for line in lines:
                    stripped_line = line.strip()
                    if stripped_line and not stripped_line.startswith('#'):
                        title = stripped_line[:100]  # Limit to 100 chars
                        break

            # Extract body (remove title and other headers)
            body_lines = []
            skip_line = False
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('#'):  # Skip headers
                    continue
                if stripped.startswith('- ') or stripped.startswith('* '):  # Keep lists
                    body_lines.append(stripped)
                elif stripped and not stripped.startswith('---') and not stripped.startswith('*Published on'):
                    body_lines.append(stripped)

            # Join body lines and clean up
            body = ' '.join(body_lines).strip()

            # Limit body length for social media
            if len(body) > 1000:  # Truncate if too long
                body = body[:1000] + "... [Read more in the full article]"

            logger.info(f"Extracted title: {title[:50]}...")
            logger.info(f"Extracted body: {body[:100]}...")

            return title, body

        except Exception as e:
            logger.error(f"Error extracting content from {markdown_file_path}: {str(e)}")
            return "", ""

    def post_to_social_media(self, title, caption):
        """
        Post content to social media platforms using the upload client
        """
        try:
            # Import the upload client
            from upload_post import UploadPostClient

            # Initialize the client with the API key
            client = UploadPostClient(api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImdvbW9wYWJvQGRlbmlwbC5jb20iLCJleHAiOjQ5MjQxNDg1ODIsImp0aSI6Ijc0ZTZlZDhiLTNlOTItNGNmYy04NjdjLTVhNTIzZWI2MmI3NiJ9.T2GNesPF54h3b6DegPNZ5vt3F_hklGtXeBAxekw4Gpk")

            # Prepare the post
            response = client.upload_photos(
                photos=[str(self.image_path)],
                title=title,
                user="ahsen",
                platforms=["x", "instagram", "linkedin"],
                caption=caption,
                visibility="PUBLIC",
                media_type="IMAGE"
            )

            logger.info(f"Upload successful: {response}")
            return True, response

        except ImportError:
            logger.error("upload_post module not found. Please install the required package.")
            return False, "upload_post module not found"
        except Exception as e:
            logger.error(f"Error posting to social media: {str(e)}")
            return False, str(e)

    def process_new_files(self):
        """
        Process any new markdown files in the posts directory
        """
        # Get all markdown files in the directory
        markdown_files = list(self.posts_directory.glob("*.md"))

        if not markdown_files:
            logger.info("No markdown files found in directory")
            return

        # Sort by modification time to get the most recent file
        latest_file = max(markdown_files, key=lambda x: x.stat().st_mtime)
        logger.info(f"Processing latest file: {latest_file.name}")

        # Check if this file has already been processed
        # We can use a simple approach: check if there's a corresponding .posted file
        posted_marker = latest_file.with_suffix('.posted')

        if posted_marker.exists():
            logger.info(f"File {latest_file.name} already posted, skipping...")
            return

        # Extract title and body
        title, caption = self.extract_title_and_body(latest_file)

        if not title or not caption:
            logger.warning(f"Could not extract title/caption from {latest_file.name}, skipping...")
            return

        # Post to social media
        success, response = self.post_to_social_media(title, caption)

        if success:
            # Create a marker file to indicate this file has been posted
            posted_marker.touch()
            logger.info(f"Successfully posted {latest_file.name} to social media")
        else:
            logger.error(f"Failed to post {latest_file.name} to social media: {response}")

    def start_monitoring(self, check_interval=60):
        """
        Start monitoring the directory for new files
        """
        logger.info(f"Starting to monitor {self.posts_directory} for new files")
        logger.info(f"Check interval: {check_interval} seconds")

        while True:
            try:
                self.process_new_files()
                time.sleep(check_interval)
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error during monitoring: {str(e)}")
                time.sleep(check_interval)


def main():
    """
    Main function to run the social poster
    """
    print("Social Poster")
    print("=" * 30)

    # Create the social poster instance
    poster = SocialPoster()

    print(f"Monitoring: {poster.posts_directory.absolute()}")
    print(f"Image file: {poster.image_path}")
    print()

    # Process any existing files immediately
    print("Processing any existing files...")
    poster.process_new_files()

    # Start monitoring
    print("Starting file monitoring...")
    print("Press Ctrl+C to stop monitoring")

    try:
        poster.start_monitoring()
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")


if __name__ == "__main__":
    main()