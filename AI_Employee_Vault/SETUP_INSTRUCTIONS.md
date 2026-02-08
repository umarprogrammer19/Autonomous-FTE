# AI Employee Vault Setup Instructions

## Bronze Tier: Personal AI Employee

Complete setup guide for your AI Employee Vault.

## Step 1: Folder Structure

The following folder structure has been created:
```
AI_Employee_Vault/
├── Inbox/
├── Needs_Action/          (Watched by the script)
├── Done/
├── Pending_Approval/
├── Approved/
├── Rejected/
├── Logs/
├── Plans/
├── Dashboard.md
├── Company_Handbook.md
├── watcher.py            (Python script to monitor Needs_Action)
└── .claude/
    └── skills/
        └── task-processor/
            └── SKILL.md  (AI skill definition)
```

## Step 2: Install Dependencies

Open a terminal/command prompt and run:
```bash
pip install watchdog
```

## Step 3: Install Claude Code

If you haven't already installed Claude Code, follow the installation instructions at the Claude Code documentation.

## Step 4: Set Up the Skill

The task-processor skill needs to be installed in your Claude Code skills directory:

1. Find your Claude Code configuration directory (usually `~/.claude/skills/` on Unix systems or `%USERPROFILE%\.claude\skills\` on Windows)
2. Copy the `.claude\skills\task-processor` folder from this vault to your Claude Code skills directory
3. Restart Claude Code to load the new skill

Alternatively, you can run Claude Code from the vault directory where the skill is already available.

## Step 5: Run the Watcher Script

From the vault directory, run:
```bash
cd "C:\Users\AHSEN\Desktop\hackathon_0\AI_Employee_Vault"
python watcher.py
```

The script will continuously monitor the `Needs_Action` folder for new `.md` files.

## Step 6: Test the System

1. With the watcher running, create a test file in the `Needs_Action` folder:
   ```
   echo "# Test Task
   Please summarize this document." > "C:\Users\AHSEN\Desktop\hackathon_0\AI_Employee_Vault\Needs_Action\test_task.md"
   ```

2. The watcher should detect the file and automatically trigger Claude Code with the `@task-processor` skill.

3. Observe as the file gets processed and moved to the appropriate folder (`Done` for simple tasks, `Pending_Approval` for complex ones).

## How It Works

1. **File Detection**: The Python script watches the `Needs_Action` folder for new `.md` files
2. **Task Processing**: When a file is detected, the `task_processor.py` script is executed
3. **Decision Making**: The script analyzes the file content and decides:
   - Simple tasks → Move to `Done` folder
   - Complex tasks → Move to `Pending_Approval` folder
   - Sensitive tasks → Create a `Plan.md` in `Plans` folder and move to `Pending_Approval`
4. **Logging**: All actions are logged in `Logs/[date].md`
5. **Dashboard**: Statistics are maintained in `Dashboard.md`

## Example Task Files

Create files in `Needs_Action` with content like:
- Simple: "Summarize the quarterly report" → Will be moved to Done
- Complex: "Research new market opportunities, analyze competition, and provide recommendations" → Will be moved to Pending_Approval
- Sensitive: "Process payment for vendor invoice #12345" → Will be moved to Pending_Approval with a Plan.md created

## Troubleshooting

- If the watcher doesn't detect files, ensure the script is running and has permission to access the directories
- If Claude Code isn't triggered, verify that Claude Code is installed and accessible from your command line
- Check the logs in the `Logs` folder for any error messages
- Make sure the task-processor skill is properly installed in Claude Code