import asyncio
import os
import subprocess
import threading
import time
from datetime import datetime
import schedule
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MasterOrchestrator:
    """
    Master Orchestrator for the AI Employee system
    Manages watchers, Claude Code integration, and scheduling
    """

    def __init__(self, vault_path="C:/Users/AHSEN/Desktop/hackathon_0/AI_Employee_Vault"):
        self.vault_path = vault_path
        self.needs_action_path = os.path.join(vault_path, "Needs_Action")
        self.pending_approval_path = os.path.join(vault_path, "Pending_Approval")
        self.approved_path = os.path.join(vault_path, "Approved")
        self.completed_path = os.path.join(vault_path, "Completed")

        # Process tracking
        self.running_processes = {}
        self.shutdown_flag = threading.Event()

    def start_watcher(self, script_path, name):
        """Start a watcher script in a separate thread"""
        def run_watcher():
            try:
                logger.info(f"Starting {name}...")
                process = subprocess.Popen(['python', script_path])
                self.running_processes[name] = process

                # Wait for process to complete (it should run indefinitely)
                process.wait()

            except Exception as e:
                logger.error(f"Error running {name}: {e}")
            finally:
                if name in self.running_processes:
                    del self.running_processes[name]

        thread = threading.Thread(target=run_watcher, daemon=True)
        thread.start()
        return thread

    def process_new_files(self):
        """Process new files in Needs_Action folder using Claude Code with @plan-creator"""
        try:
            needs_action_files = [f for f in os.listdir(self.needs_action_path)
                                  if f.endswith('.md') and not f.startswith('.')]

            for filename in needs_action_files:
                filepath = os.path.join(self.needs_action_path, filename)

                # Skip if file is currently being written to
                if self.is_file_locked(filepath):
                    continue

                logger.info(f"Processing new file: {filename}")

                # Create a plan for the task using Claude Code
                self.create_plan_for_task(filepath, filename)

        except Exception as e:
            logger.error(f"Error processing new files: {e}")

    def is_file_locked(self, filepath):
        """Check if a file is currently locked/writing"""
        try:
            with open(filepath, 'r+'):
                pass
            return False
        except IOError:
            return True

    def create_plan_for_task(self, filepath, filename):
        """Create a plan for a task using Claude Code @plan-creator skill"""
        try:
            # Read the file content to understand the task
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # For simplicity in this implementation, we'll create a basic plan file
            # In a real implementation, this would call Claude Code with @plan-creator
            plan_filename = f"plan_{filename.replace('.md', '.md')}"
            plan_filepath = os.path.join(self.vault_path, "Plans", plan_filename)

            # Create a basic plan based on the content
            plan_content = f"""# Task Plan: {filename.replace('.md', '').replace('_', ' ').title()}

## Overview
This plan was generated for the task described in {filename}.
Based on the content: "{content[:200]}..."

## Prerequisites
- [ ] Review original task file: {filename}
- [ ] Gather any additional context needed

## Action Steps
- [ ] Analyze the task requirements
- [ ] Determine if human approval is needed
- [ ] Execute appropriate action based on task type
- [ ] Update task status appropriately

## Success Criteria
- [ ] Task completed according to requirements
- [ ] Proper documentation created
- [ ] Status updated correctly

## Risk Assessment
- [ ] Identify potential obstacles
- [ ] Plan mitigation strategies if needed

## Time Estimate
- Analysis: 10-15 minutes
- Execution: Variable based on task
- Documentation: 5-10 minutes

## Approval Status
- Required approvals: 1 for sensitive tasks
- Current status: Pending initial review
"""

            # Write the plan file
            os.makedirs(os.path.dirname(plan_filepath), exist_ok=True)
            with open(plan_filepath, 'w', encoding='utf-8') as f:
                f.write(plan_content)

            logger.info(f"Created plan file: {plan_filepath}")

            # Determine if the task needs approval based on content
            needs_approval = self.determine_approval_needed(content)

            if needs_approval:
                # Move to Pending Approval
                approval_filepath = os.path.join(self.pending_approval_path, filename)
                os.rename(filepath, approval_filepath)
                logger.info(f"Moved {filename} to Pending Approval")
            else:
                # Process directly
                self.process_approved_task(filepath, filename)

        except Exception as e:
            logger.error(f"Error creating plan for {filename}: {e}")

    def determine_approval_needed(self, content):
        """Determine if a task needs human approval based on content"""
        approval_keywords = [
            'urgent', 'important', 'sensitive', 'client', 'customer',
            'payment', 'money', 'financial', 'contract', 'agreement',
            'private', 'confidential', 'personal', 'linkedin', 'social'
        ]

        content_lower = content.lower()
        for keyword in approval_keywords:
            if keyword in content_lower:
                return True

        return False

    def process_approved_task(self, filepath, filename):
        """Process an approved task"""
        try:
            # In a real implementation, this would trigger MCP services
            # For now, we'll just move the file to completed
            completed_filepath = os.path.join(self.completed_path, f"{filename}.completed_{int(time.time())}")
            os.rename(filepath, completed_filepath)
            logger.info(f"Processed and moved {filename} to Completed")

        except Exception as e:
            logger.error(f"Error processing approved task {filename}: {e}")

    def setup_scheduled_tasks(self):
        """Setup scheduled tasks using the schedule library"""
        # Schedule file processing every 5 minutes
        schedule.every(5).minutes.do(self.process_new_files)

        # Schedule daily summary at 9 AM
        schedule.every().day.at("09:00").do(self.daily_summary)

        # Schedule weekly cleanup on Sundays at midnight
        schedule.every().sunday.at("00:00").do(self.weekly_cleanup)

    def daily_summary(self):
        """Generate daily summary of activities"""
        try:
            needs_action_count = len([f for f in os.listdir(self.needs_action_path) if f.endswith('.md')])
            pending_count = len([f for f in os.listdir(self.pending_approval_path) if f.endswith('.md')])
            approved_count = len([f for f in os.listdir(self.approved_path) if f.endswith('.md')])
            completed_count = len([f for f in os.listdir(self.completed_path) if f.endswith('.md')])

            summary = f"""# Daily Summary - {datetime.now().strftime('%Y-%m-%d')}

## Task Statistics
- Files needing action: {needs_action_count}
- Pending approvals: {pending_count}
- Approved tasks: {approved_count}
- Completed tasks: {completed_count}

## Next Steps
- Review pending approvals
- Process urgent tasks
- Update dashboard

Generated at {datetime.now().strftime('%H:%M:%S')}
"""

            summary_path = os.path.join(self.vault_path, f"daily_summary_{datetime.now().strftime('%Y%m%d')}.md")
            with open(summary_path, 'w') as f:
                f.write(summary)

            logger.info("Daily summary generated")

        except Exception as e:
            logger.error(f"Error generating daily summary: {e}")

    def weekly_cleanup(self):
        """Perform weekly cleanup tasks"""
        try:
            logger.info("Performing weekly cleanup...")

            # Archive old completed tasks (older than 30 days)
            completed_dir = Path(self.completed_path)
            current_time = time.time()

            for file_path in completed_dir.iterdir():
                if file_path.is_file() and file_path.suffix == '.md':
                    # If file is older than 30 days, archive it
                    if current_time - file_path.stat().st_mtime > 30 * 24 * 3600:
                        archive_dir = os.path.join(self.vault_path, "Archive")
                        os.makedirs(archive_dir, exist_ok=True)

                        archive_path = os.path.join(archive_dir, f"archived_{file_path.name}")
                        os.rename(file_path, archive_path)
                        logger.info(f"Archived old file: {file_path.name}")

            logger.info("Weekly cleanup completed")

        except Exception as e:
            logger.error(f"Error during weekly cleanup: {e}")

    def run_scheduler(self):
        """Run the scheduler in a separate thread"""
        def run_schedule():
            while not self.shutdown_flag.is_set():
                schedule.run_pending()
                time.sleep(1)

        scheduler_thread = threading.Thread(target=run_schedule, daemon=True)
        scheduler_thread.start()
        return scheduler_thread

    def run(self):
        """Main run method to start the orchestrator"""
        logger.info("Starting Master Orchestrator...")

        # Setup directories
        os.makedirs(self.needs_action_path, exist_ok=True)
        os.makedirs(self.pending_approval_path, exist_ok=True)
        os.makedirs(self.approved_path, exist_ok=True)
        os.makedirs(self.completed_path, exist_ok=True)
        os.makedirs(os.path.join(self.vault_path, "Plans"), exist_ok=True)

        # Start watchers
        gmail_watcher_path = os.path.join(os.path.dirname(__file__), "gmail_watcher.py")
        whatsapp_watcher_path = os.path.join(os.path.dirname(__file__), "whatsapp_watcher.py")

        if os.path.exists(gmail_watcher_path):
            self.start_watcher(gmail_watcher_path, "Gmail Watcher")
            logger.info("Started Gmail Watcher")
        else:
            logger.warning("Gmail Watcher script not found")

        if os.path.exists(whatsapp_watcher_path):
            self.start_watcher(whatsapp_watcher_path, "WhatsApp Watcher")
            logger.info("Started WhatsApp Watcher")
        else:
            logger.warning("WhatsApp Watcher script not found")

        # Setup scheduled tasks
        self.setup_scheduled_tasks()
        scheduler_thread = self.run_scheduler()
        logger.info("Scheduler started")

        # Main loop
        try:
            while not self.shutdown_flag.is_set():
                # Process new files in Needs_Action
                self.process_new_files()

                # Check for approved files to process
                self.check_approved_tasks()

                time.sleep(10)  # Wait 10 seconds before next cycle

        except KeyboardInterrupt:
            logger.info("Master Orchestrator shutting down...")
            self.shutdown_flag.set()

    def check_approved_tasks(self):
        """Check for approved tasks in the Approved folder"""
        try:
            approved_files = [f for f in os.listdir(self.approved_path)
                             if f.endswith('.md') and not f.startswith('.')]

            for filename in approved_files:
                filepath = os.path.join(self.approved_path, filename)

                # Skip if file is currently being written to
                if self.is_file_locked(filepath):
                    continue

                logger.info(f"Processing approved file: {filename}")

                # Process the approved task
                completed_filepath = os.path.join(self.completed_path, f"{filename}.processed_{int(time.time())}")
                os.rename(filepath, completed_filepath)
                logger.info(f"Processed approved task: {filename}")

        except Exception as e:
            logger.error(f"Error checking approved tasks: {e}")


if __name__ == "__main__":
    orchestrator = MasterOrchestrator()
    orchestrator.run()