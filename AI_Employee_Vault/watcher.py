import os
import time
import subprocess
import logging
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

VAULT_PATH = r"C:\Users\AHSEN\Desktop\hackathon_0\AI_Employee_Vault"
NEEDS_ACTION_PATH = os.path.join(VAULT_PATH, "Needs_Action")
LOGS_PATH = os.path.join(VAULT_PATH, "Logs")

class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        # Check if it's a markdown file
        if event.src_path.lower().endswith('.md'):
            logger.info(f"New file detected: {event.src_path}")
            self.process_new_file(event.src_path)

    def on_moved(self, event):
        if event.is_directory:
            return

        # Also handle moved files (in case files are moved to Needs_Action)
        if event.dest_path.lower().endswith('.md') and NEEDS_ACTION_PATH in event.dest_path:
            logger.info(f"File moved to Needs_Action: {event.dest_path}")
            self.process_new_file(event.dest_path)

    def process_new_file(self, file_path):
        """Process the new file with Claude Code"""
        try:
            logger.info("Processing with Claude...")

            # Prepare the command to run the task processor Python script
            cmd_str = f'python "{VAULT_PATH}\\task_processor.py" "{file_path}"'

            # Execute the command
            result = subprocess.run(
                cmd_str,
                cwd=VAULT_PATH,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                shell=True   # Added for Windows compatibility
            )

            if result.returncode == 0:
                logger.info(f"Successfully processed file: {file_path}")
                logger.info(f"Output: {result.stdout}")
            else:
                logger.error(f"Error processing file: {file_path}")
                logger.error(f"Error: {result.stderr}")

        except subprocess.TimeoutExpired:
            logger.error(f"Processing timed out for file: {file_path}")
        except Exception as e:
            logger.error(f"Exception occurred while processing file {file_path}: {str(e)}")

def ensure_logs_directory():
    """Ensure the logs directory exists"""
    if not os.path.exists(LOGS_PATH):
        os.makedirs(LOGS_PATH)
        logger.info(f"Created logs directory: {LOGS_PATH}")

def main():
    ensure_logs_directory()

    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, NEEDS_ACTION_PATH, recursive=False)

    logger.info(f"Starting file watcher for: {NEEDS_ACTION_PATH}")
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("File watcher stopped.")

    observer.join()

if __name__ == "__main__":
    main()