import time
import os
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Define our folders
DROP_ZONE = "AI_Employee_Vault/Drop_Zone"
NEEDS_ACTION = "AI_Employee_Vault/Needs_Action"


class DropFolderHandler(FileSystemEventHandler):
    def on_created(self, event):
        # Ignore if a folder is created, we only care about files
        if event.is_directory:
            return

        # Get the file that was just dropped
        source_path = event.src_path
        filename = os.path.basename(source_path)

        print(f"👀 Watcher spotted a new file: {filename}")

        # Give it a second to finish copying
        time.sleep(1)

        # We don't just move the file, we create a specific task file for Qwen
        task_filename = f"TASK_{filename}.md"
        task_filepath = os.path.join(NEEDS_ACTION, task_filename)

        print(f"📝 Writing instructions for Qwen into: {task_filename}")

        # Write the instructions for the AI
        with open(task_filepath, "w", encoding="utf-8") as f:
            f.write(f"---\n")
            f.write(f"type: file_drop\n")
            f.write(f"original_file: {filename}\n")
            f.write(f"---\n\n")
            f.write(f"A new file named '{filename}' was dropped into the Drop Zone.\n")
            f.write(
                f"Please analyze it and decide what to do with it based on your Company Handbook.\n"
            )

        # Move the original file out of the drop zone so we don't process it twice
        os.remove(source_path)
        print("✅ Task successfully handed off to the /Needs_Action inbox!")


def start_watching():
    print(f"👁️  Watcher started. Keeping an eye on the {DROP_ZONE} folder...")

    event_handler = DropFolderHandler()
    observer = Observer()
    observer.schedule(event_handler, DROP_ZONE, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    start_watching()
