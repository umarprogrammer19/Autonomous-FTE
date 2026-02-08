"""
Test script for the Daily AI Post Scheduler
"""

import os
from pathlib import Path
from daily_ai_scheduler import DailyAIPostScheduler


def test_scheduler():
    """
    Test the Daily AI Post Scheduler functionality
    """
    print("Testing Daily AI Post Scheduler")
    print("=" * 40)

    # Create scheduler instance
    scheduler = DailyAIPostScheduler()

    print(f"[SUCCESS] Scheduler initialized successfully")
    print(f"[INFO] Posts directory: {scheduler.posts_directory.absolute()}")

    # Check if directory exists
    if scheduler.posts_directory.exists():
        print(f"[SUCCESS] Posts directory exists")
    else:
        print(f"[ERROR] Posts directory does not exist")

    # Test the scheduled task (runs once)
    print(f"\nTesting scheduled task execution...")
    success = scheduler.run_once_now()

    if success:
        print(f"[SUCCESS] Scheduled task completed successfully")
    else:
        print(f"[ERROR] Scheduled task failed")

    # Check for created files
    posts_dir = Path("Daily_AI_Posts")
    if posts_dir.exists():
        files = list(posts_dir.glob("*.md"))
        print(f"\nFiles in posts directory: {len(files)}")
        for file in files:
            print(f"  - {file.name}")

    print(f"\nTest completed!")


if __name__ == "__main__":
    test_scheduler()