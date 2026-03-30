import os
import time
import shutil
import subprocess

# Define our exact folder paths based on your workspace
VAULT = "AI_Employee_Vault"
NEEDS_ACTION_DIR = os.path.join(VAULT, "Needs_Action")
APPROVED_DIR = os.path.join(VAULT, "Approved")
DONE_DIR = os.path.join(VAULT, "Done")
PENDING_DIR = os.path.join(VAULT, "Pending_Approval")


def process_folder(folder_name, context_prompt):
    # Make sure the folder exists so we don't get errors
    if not os.path.exists(folder_name):
        return

    for filename in os.listdir(folder_name):
        if filename.endswith(".md"):
            filepath = os.path.join(folder_name, filename)
            print(f"\n📂 New file found in {folder_name}: {filename}")
            print("⚡ Waking up Qwen Code...")

            with open(filepath, "r", encoding="utf-8") as file:
                task_content = file.read()

            # We inject the safety rules directly into Qwen's brain
            safety_rules = f"CRITICAL SAFETY RULES: If the task requires a SENSITIVE ACTION (like deleting a record, sending an email, or making a payment), YOU MUST NOT EXECUTE IT. Instead, you must write a brief markdown file explaining what you intend to do, and save it in the '{PENDING_DIR}' folder. Do not proceed until the human approves it."

            # Combine everything into one string
            raw_prompt = f"{context_prompt} {safety_rules} Task details: {task_content} Do not ask for human input in the terminal, just execute."

            # THE FIX: Remove all line breaks and double quotes so Windows doesn't choke on it
            safe_prompt = (
                raw_prompt.replace("\n", " ").replace("\r", "").replace('"', "'")
            )

            # Pass the single safe line to Qwen (No shell=True needed!)
            subprocess.run(["qwen.cmd", "-y", "-p", safe_prompt])

            # Move to Done
            done_path = os.path.join(DONE_DIR, filename)
            shutil.move(filepath, done_path)
            print(f"✅ Task complete! Moved {filename} to the Done folder.")


def run_manager():
    print("🤖 Orchestrator started. Watching Needs_Action AND Approved folders 24/7...")

    # Ensure all our desk folders actually exist
    for folder in [NEEDS_ACTION_DIR, APPROVED_DIR, DONE_DIR, PENDING_DIR]:
        os.makedirs(folder, exist_ok=True)

    while True:
        # 1. Check for new incoming tasks
        process_folder(NEEDS_ACTION_DIR, "You have a new task to process.")

        # 2. Check for dangerous tasks the boss just gave permission to execute
        process_folder(
            APPROVED_DIR,
            "The boss has APPROVED this action. The safety rules are temporarily lifted for this specific task. Please execute exactly what is requested using your Odoo tools.",
        )

        time.sleep(10)


if __name__ == "__main__":
    run_manager()
