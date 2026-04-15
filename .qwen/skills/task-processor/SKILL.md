# Task Processor Skill

This skill processes files from the Needs_Action folder, makes decisions about how to handle them, and moves them to the appropriate folder.

## Functionality

- Reads and analyzes the content of the file
- Determines if the task is simple, complex, or sensitive
- Moves files to appropriate destination folders:
  - Simple tasks → Done
  - Complex tasks → Pending_Approval
  - Sensitive tasks → Pending_Approval with Plan.md creation
- Creates log entries in the Logs folder
- Updates Dashboard statistics

## Processing Logic

1. **Analyze Content**: Determine the nature of the task in the file
2. **Classify Task**:
   - Simple: Routine tasks that can be completed automatically
   - Complex: Tasks requiring multiple steps or decision points
   - Sensitive: Tasks involving payments, personal data, or security
3. **Take Action**:
   - For simple tasks: Process and move to Done
   - For complex tasks: Move to Pending_Approval
   - For sensitive tasks: Create Plan.md in Plans folder and move to Pending_Approval
4. **Log Action**: Record the action in the daily log file
5. **Update Dashboard**: Increment statistics

## Usage

`@task-processor process this file: [file path]`

## Implementation

```python
import os
import shutil
from datetime import datetime

def process_task_file(file_path):
    """
    Process a task file based on its content and move it to the appropriate folder.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Determine the action based on content analysis
    destination_folder, needs_plan = classify_task(content)

    # Move the file to the appropriate folder
    move_file(file_path, destination_folder)

    # Create Plan.md if needed (for sensitive tasks)
    if needs_plan:
        create_plan_file(file_path, content)

    # Log the action
    log_action(file_path, destination_folder, needs_plan)

    # Update dashboard stats
    update_dashboard_stats(destination_folder)

    return f"Processed {file_path} -> {destination_folder}"

def classify_task(content):
    """
    Classify the task based on its content.
    Returns: (destination_folder, needs_plan)
    """
    content_lower = content.lower()

    # Check for sensitive keywords
    sensitive_keywords = ['payment', 'salary', 'payroll', 'password', 'credit card', 'bank', 'financial', 'private', 'confidential']
    if any(keyword in content_lower for keyword in sensitive_keywords):
        return "Pending_Approval", True

    # Check for complex keywords
    complex_keywords = ['approval needed', 'multiple steps', 'research required', 'consult team', 'requires analysis']
    if any(keyword in content_lower for keyword in complex_keywords):
        return "Pending_Approval", False

    # Simple task by default
    return "Done", False

def move_file(source_path, destination_folder):
    """
    Move the file from source to destination folder.
    """
    vault_path = os.path.dirname(os.path.dirname(os.path.dirname(source_path)))  # Go up 3 levels to vault
    dest_path = os.path.join(vault_path, destination_folder, os.path.basename(source_path))
    shutil.move(source_path, dest_path)

def create_plan_file(original_file_path, content):
    """
    Create a Plan.md file in the Plans folder for sensitive tasks.
    """
    vault_path = os.path.dirname(os.path.dirname(os.path.dirname(original_file_path)))
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

def log_action(file_path, destination, needs_plan):
    """
    Log the action in the daily log file.
    """
    vault_path = os.path.dirname(os.path.dirname(os.path.dirname(file_path)))
    logs_folder = os.path.join(vault_path, "Logs")

    today = datetime.now().strftime("%Y-%m-%d")
    log_path = os.path.join(logs_folder, f"{today}.md")

    log_entry = f"- {datetime.now().strftime('%H:%M:%S')} - Moved '{os.path.basename(file_path)}' to '{destination}'{' with Plan.md' if needs_plan else ''}\n"

    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(log_entry)

def update_dashboard_stats(destination_folder):
    """
    Update dashboard statistics.
    """
    # This would update the Dashboard.md file with statistics
    # Implementation details would depend on how stats are tracked
    pass
```