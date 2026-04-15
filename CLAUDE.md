# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Social Media AI Employee** - a comprehensive social media automation platform built with NiceGUI. It combines email campaigns, WhatsApp messaging, and AI-powered social media content generation through a unified web dashboard. The system includes an AI Employee Vault workflow for task processing with human-in-the-loop approval.

## Common Commands

### Run the Application
```bash
python app_nicegui_enhanced.py
```
Access the dashboard at `http://localhost:8080`.

### Setup and Dependencies
```bash
# Install dependencies
uv sync

# Setup (creates .env from .env.example if missing)
python setup.py
```

### Run Schedulers
```bash
# Daily AI post scheduler (runs every 24 hours)
python daily_ai_scheduler.py

# Run once (test mode)
python daily_ai_scheduler.py --test

# Combined scheduler (email + WhatsApp)
python combined_scheduler.py

# Social poster (monitors and posts content)
python social_poster.py
```

### Run Tests
```bash
python test_functionality.py
python test_whatsapp_automation.py
python test_scheduler.py
python test_sender.py
```

### AI Employee Vault Operations
```bash
# Start the vault watcher (monitors Needs_Action folder)
python AI_Employee_Vault/watcher.py

# Start the master orchestrator
python orchestrator.py

# Start Gmail watcher
python gmail_watcher.py

# Start WhatsApp watcher
python whatsapp_watcher.py
```

### Send Messages (CLI)
```bash
# Send WhatsApp message
python whatsapp_sender.py "PHONE_NUMBER" "MESSAGE"

# Send email
python email_mcp_server.py "recipient@email.com" "Subject" "Message body"
```

## Architecture

### Main Application (`app_nicegui_enhanced.py`)
- Built with **NiceGUI** for a modern web interface
- Uses `AppState` class for global state management
- Sidebar navigation: Dashboard, Email Sender, WhatsApp Manager, AI Post Generator, Settings
- Real-time analytics display via `analytics_tracker.py`

### Services Layer (`services/`)
Services communicate via subprocess calls to standalone scripts:

- **`email_service.py`** → calls `email_mcp_server.py` (SMTP via Gmail)
- **`whatsapp_service.py`** → calls `whatsapp_sender.py` (whapi.cloud HTTP API)
- **`ai_post_service.py`** → calls `daily_ai_scheduler.py` (AI post generation)

### Schedulers and Background Tasks
- **`daily_ai_scheduler.py`**: Generates AI posts every 24 hours using `schedule` library
- **`combined_scheduler.py`**: Manages combined email/WhatsApp campaigns
- **`social_poster.py`**: Monitors `Daily_AI_Posts/` and posts to social platforms

### AI Employee Vault Workflow
Located in `AI_Employee_Vault/`:

1. **Needs_Action/**: Incoming tasks (Gmail, WhatsApp, manual creation)
2. **Plans/**: Generated Plan.md files with checkboxes before execution
3. **Pending_Approval/**: Tasks awaiting human review
4. **Done/**: Completed tasks
5. **Logs/**: Daily activity logs

**Processing Flow**:
- `watcher.py` monitors `Needs_Action/` for new `.md` files
- `task_processor.py` processes tasks using Claude Code
- `orchestrator.py` manages watchers and scheduling
- Complex/sensitive tasks require Plan.md before execution

### Data Storage
- `data/contacts.json`: WhatsApp contact list
- `data/analytics.json`: Email/WhatsApp/AI post metrics
- `data/post_history.json`: Generated AI posts
- `Daily_AI_Posts/`: Markdown posts with `.posted` marker files
- `logs/`: Application logs

### Environment Variables
Required in `.env`:
- `EMAIL_ADDRESS`, `EMAIL_APP_PASSWORD`, `SMTP_SERVER`, `SMTP_PORT`
- `WHAPI_TOKEN` (from whapi.cloud)
- `WHAPI_BASE_URL` (default: https://gate.whapi.cloud)

### Key Design Patterns
- **Subprocess-based services**: Services spawn Python scripts rather than direct imports
- **File-based state**: JSON/markdown files for persistence (not a database)
- **Polling/watchdog patterns**: File system watchers and API polling for event handling
- **Human-in-the-loop**: Approval workflow via Pending_Approval folder before execution