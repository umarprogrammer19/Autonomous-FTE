"""
Test script for the combined scheduler and social poster functionality
"""

import os
from pathlib import Path
from combined_scheduler import CombinedScheduler
from daily_ai_scheduler import DailyAIPostScheduler
from social_poster import SocialPoster


def test_combined_functionality():
    """
    Test the combined functionality of scheduler and social poster
    """
    print("Testing Combined Scheduler and Social Poster")
    print("=" * 50)

    # Create a test instance
    scheduler = CombinedScheduler()

    print(f"[SUCCESS] Combined scheduler initialized")
    print(f"[INFO] Posts directory: {scheduler.posts_directory.absolute()}")
    print(f"[INFO] Image path: {scheduler.image_path}")

    # Test AI scheduler
    ai_scheduler = DailyAIPostScheduler()
    print(f"[SUCCESS] AI Scheduler initialized")

    # Test social poster
    social_poster = SocialPoster()
    print(f"[SUCCESS] Social Poster initialized")

    # Test the AI post generation (runs once)
    print(f"\nTesting AI post generation...")
    success = ai_scheduler.run_once_now()

    if success:
        print(f"[SUCCESS] AI post generation completed successfully")
    else:
        print(f"[INFO] AI post generation completed with some issues")

    # Check for created files
    posts_dir = Path("Daily_AI_Posts")
    if posts_dir.exists():
        files = list(posts_dir.glob("*.md"))
        print(f"\nFiles in posts directory: {len(files)}")
        for file in files:
            print(f"  - {file.name}")

        # Test social posting with the latest file
        if files:
            latest_file = max(files, key=lambda x: x.stat().st_mtime)
            print(f"\nTesting social posting for: {latest_file.name}")

            # Extract title and body
            title, caption = social_poster.extract_title_and_body(latest_file)

            print(f"  Title: {title[:50]}{'...' if len(title) > 50 else ''}")
            print(f"  Caption preview: {caption[:100]}{'...' if len(caption) > 100 else ''}")

    print(f"\nTest completed!")


if __name__ == "__main__":
    test_combined_functionality()