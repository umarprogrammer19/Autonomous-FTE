import os
import time
import shutil
import subprocess

# Define our folders
NEEDS_ACTION_DIR = "AI_Employee_Vault/Needs_Action"
APPROVED_DIR = "AI_Employee_Vault/Approved"
DONE_DIR = "AI_Employee_Vault/Done"


def process_folder(folder_name, context_prompt):
    # This function looks inside a specific folder and processes any .md files
    for filename in os.listdir(folder_name):
        if filename.endswith(".md"):
            filepath = os.path.join(folder_name, filename)
            print(f"\n📂 New file found in {folder_name}: {filename}")
            print("⚡ Waking up Qwen Code...")

            with open(filepath, "r", encoding="utf-8") as file:
                task_content = file.read()

            # Combine our specific instructions with the file's content
            prompt = f"{context_prompt} Read the Company_Handbook.md for your rules. Task details: {task_content}. Do not ask for human input, just execute it."

            # Launch Qwen
            subprocess.run(["qwen.cmd", prompt], shell=True)

            # Move to Done
            done_path = os.path.join(DONE_DIR, filename)
            shutil.move(filepath, done_path)
            print(f"✅ Task complete! Moved {filename} to the Done folder.")


def run_manager():
    print("🤖 Orchestrator started. Watching Needs_Action AND Approved folders 24/7...")

    while True:
        # 1. Check for brand new tasks coming in from the Watchers
        process_folder(NEEDS_ACTION_DIR, "You have a new task.")

        # 2. Check for dangerous tasks the boss just gave permission to execute
        process_folder(
            APPROVED_DIR,
            "The boss has APPROVED this action. Please execute exactly what is requested in this file using your Odoo MCP tools.",
        )

        # Breathe for 10 seconds
        time.sleep(10)


if __name__ == "__main__":
    run_manager()
