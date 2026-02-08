import os
import shutil
import sys
from datetime import datetime

def process_task_file(file_path):
    """
    Process a task file based on its content and move it to the appropriate folder.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Determine the action based on content analysis
    destination_folder, needs_plan = classify_task(content)

    # Get the vault path from the file path
    # Assuming the structure: VAULT_PATH/folder/filename
    vault_path = os.path.dirname(os.path.dirname(file_path))  # Go up 2 levels to vault

    # Move the file to the appropriate folder
    move_file(file_path, destination_folder, vault_path)

    # Create Plan.md if needed (for sensitive tasks)
    if needs_plan:
        create_plan_file(file_path, content, vault_path)

    # Log the action
    log_action(file_path, destination_folder, needs_plan, vault_path)

    # Update dashboard stats
    update_dashboard_stats(destination_folder, vault_path)

    print(f"Processed {os.path.basename(file_path)} -> {destination_folder}")

def classify_task(content):
    """
    Classify the task based on its content.
    Returns: (destination_folder, needs_plan)
    """
    content_lower = content.lower()

    # Check for sensitive keywords
    sensitive_keywords = ['payment', 'salary', 'payroll', 'password', 'credit card', 'bank', 'financial', 'private', 'confidential', 'sensitive']
    if any(keyword in content_lower for keyword in sensitive_keywords):
        return "Pending_Approval", True

    # Check for complex keywords
    complex_keywords = ['approval needed', 'multiple steps', 'research required', 'consult team', 'requires analysis', 'complex', 'complicated']
    if any(keyword in content_lower for keyword in complex_keywords):
        return "Pending_Approval", False

    # Simple task by default
    return "Done", False

def move_file(source_path, destination_folder, vault_path):
    """
    Move the file from source to destination folder.
    """
    dest_path = os.path.join(vault_path, destination_folder, os.path.basename(source_path))
    shutil.move(source_path, dest_path)

def create_plan_file(original_file_path, content, vault_path):
    """
    Create a Plan.md file in the Plans folder for sensitive tasks.
    """
    plans_folder = os.path.join(vault_path, "Plans")

    # Create filename based on original file
    original_filename = os.path.splitext(os.path.basename(original_file_path))[0]
    plan_filename = f"{original_filename}_Plan.md"
    plan_path = os.path.join(plans_folder, plan_filename)

    plan_content = f"""# Plan for {original_filename}

## Original Request
{content}

## Required Actions
- [ ] Action 1
- [ ] Action 2
- [ ] Action 3

## Approval Status
- [ ] Reviewed by human
- [ ] Approved for execution
- [ ] Completed

## Notes
Any additional notes about the execution of this plan.
"""

    with open(plan_path, 'w', encoding='utf-8') as f:
        f.write(plan_content)

def log_action(file_path, destination, needs_plan, vault_path):
    """
    Log the action in the daily log file.
    """
    logs_folder = os.path.join(vault_path, "Logs")

    today = datetime.now().strftime("%Y-%m-%d")
    log_path = os.path.join(logs_folder, f"{today}.md")

    log_entry = f"- {datetime.now().strftime('%H:%M:%S')} - Moved '{os.path.basename(file_path)}' to '{destination}'{' with Plan.md' if needs_plan else ''}\n"

    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(log_entry)

def update_dashboard_stats(destination_folder, vault_path):
    """
    Update dashboard statistics.
    """
    dashboard_path = os.path.join(vault_path, "Dashboard.md")

    # Read the current dashboard
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # This is a simplified update - in a real implementation you'd want to parse and update stats properly
    # For now, we'll just note that we processed a file
    print(f"Updated dashboard statistics for {destination_folder} task")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python task_processor.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)

    process_task_file(file_path)