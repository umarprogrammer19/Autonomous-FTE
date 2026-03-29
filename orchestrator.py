import os
import time
import shutil
import subprocess

# folders
NEEDS_ACTION_DIR = "AI_Employee_Vault/Needs_Action"
DONE_DIR = "AI_Employee_Vault/Done"


def run_manager():
    print("🤖 Orchestrator started. Watching the Needs_Action folder 24/7...")

    while True:
        # Look at every file in the Needs_Action folder
        for filename in os.listdir(NEEDS_ACTION_DIR):
            if filename.endswith(".md"):
                filepath = os.path.join(NEEDS_ACTION_DIR, filename)
                print(f"\n📂 New task found: {filename}")
                print("⚡ Waking up Qwen Code...")

                # We read the task instructions
                with open(filepath, "r", encoding="utf-8") as file:
                    task_content = file.read()

                # We tell Qwen exactly what to do using a background prompt
                prompt = f"Execute the following task using your Odoo MCP tools and skills. Task: {task_content}. Do not ask for human input, just execute it."

                # THE FIX: Added 'qwen.cmd' and 'shell=True' for Windows compatibility
                subprocess.run(["qwen.cmd", prompt], shell=True)

                # Once Qwen finishes and closes, we move the file to Done
                done_path = os.path.join(DONE_DIR, filename)
                shutil.move(filepath, done_path)
                print(f"✅ Task complete! Moved {filename} to the Done folder.")

        # Take a 10-second breath before checking the folder again
        time.sleep(10)


if __name__ == "__main__":
    run_manager()
