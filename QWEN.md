# Social Media AI Employee - Project Context

## Project Overview

This is a **Social Media AI Employee** - a comprehensive social media automation platform built with **NiceGUI**. It combines email campaigns, WhatsApp messaging, and AI-powered social media content generation through a unified web dashboard accessible at `http://localhost:8080`.

The system features an **AI Employee Vault** workflow for task processing with human-in-the-loop approval, allowing automated task handling from Gmail and WhatsApp inputs.

## Key Technologies

- **Python 3.8+** (primary language)
- **NiceGUI** - Web UI framework
- **whapi.cloud HTTP API** - WhatsApp messaging (no browser automation)
- **SMTP/Gmail** - Email sending
- **Schedule library** - Background task scheduling
- **File-based state** - JSON/Markdown persistence (no database)

## Architecture

### Folder Structure
```
Social_Media_AI_Employee/
├── app_nicegui_enhanced.py          # Main NiceGUI application (entry point)
├── services/
│   ├── email_service.py             # Email service (subprocess wrapper)
│   ├── whatsapp_service.py          # WhatsApp service (subprocess wrapper)
│   └── ai_post_service.py           # AI post generation service
├── AI_Employee_Vault/
│   ├── Needs_Action/                # Incoming tasks
│   ├── Plans/                       # Generated Plan.md files
│   ├── Pending_Approval/            # Tasks awaiting review
│   ├── Done/                        # Completed tasks
│   ├── Logs/                        # Activity logs
│   ├── watcher.py                   # File system watcher
│   ├── task_processor.py            # Task processing with Claude Code
│   └── Company_Handbook.md          # Company documentation
├── Daily_AI_Posts/                  # AI-generated social media posts
├── data/                            # Runtime data (contacts, analytics, posts)
├── logs/                            # Application logs
├── daily_ai_scheduler.py            # 24-hour AI post scheduler
├── combined_scheduler.py            # Email + WhatsApp campaign scheduler
├── social_poster.py                 # Posts content to social platforms
├── analytics_tracker.py             # Metrics tracking
├── email_mcp_server.py              # Standalone email script
├── whatsapp_sender.py               # Standalone WhatsApp sender
├── whatsapp_automation.py           # WhatsApp auto-reply system
├── whatsapp_cli.py                  # CLI for WhatsApp operations
├── orchestrator.py                  # Master orchestrator for vault
├── gmail_watcher.py                 # Gmail task watcher
├── whatsapp_watcher.py              # WhatsApp task watcher
└── requirements.txt                 # Dependencies
```

### Service Layer Pattern

Services use **subprocess calls** to standalone scripts rather than direct imports:

| Service | Calls Script |
|---------|-------------|
| `EmailService.send_email()` | `email_mcp_server.py` |
| `WhatsAppService.send_message()` | `whatsapp_sender.py` |
| `AIPostService.generate_and_post_now()` | `daily_ai_scheduler.py --test` |

### AI Employee Vault Workflow

1. **Needs_Action/**: Incoming tasks arrive here (from Gmail, WhatsApp, or manual creation)
2. **Plans/**: Generated `Plan.md` files with checkboxes before execution
3. **Pending_Approval/**: Tasks awaiting human review
4. **Done/**: Completed tasks
5. **Logs/**: Daily activity logs

Processing flow:
- `watcher.py` monitors `Needs_Action/` for new `.md` files
- `task_processor.py` processes tasks using Claude Code
- `orchestrator.py` manages watchers and scheduling
- Complex/sensitive tasks require Plan.md before execution

## Common Commands

### Run the Application
```bash
python app_nicegui_enhanced.py
```
Access dashboard at `http://localhost:8080`.

### Setup and Dependencies
```bash
# Install dependencies
pip install -r requirements.txt
# Or use uv
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

# Combined scheduler (email + WhatsApp campaigns)
python combined_scheduler.py

# Social poster (monitors Daily_AI_Posts/ and posts)
python social_poster.py
```

### Run AI Employee Vault
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

### CLI Operations
```bash
# Send WhatsApp message
python whatsapp_sender.py "PHONE_NUMBER" "MESSAGE"
# Or via CLI wrapper
python whatsapp_cli.py send 923182710120 "Hello!"

# Send email
python email_mcp_server.py "recipient@email.com" "Subject" "Message body"

# Start WhatsApp automation
python whatsapp_cli.py start
python whatsapp_cli.py start --webhook
```

### Run Tests
```bash
python test_functionality.py
python test_whatsapp_automation.py
python test_scheduler.py
python test_sender.py
python test_combined.py
```

## Environment Variables

Required in `.env` (copy from `.env.example`):

### Email Configuration
| Variable | Description |
|----------|-------------|
| `EMAIL_ADDRESS` | Gmail address |
| `EMAIL_APP_PASSWORD` | Gmail app password |
| `SMTP_SERVER` | SMTP server (e.g., smtp.gmail.com) |
| `SMTP_PORT` | SMTP port (e.g., 587) |

### WhatsApp Configuration
| Variable | Description | Default |
|----------|-------------|---------|
| `WHAPI_TOKEN` | whapi.cloud API token | N/A |
| `WHAPI_BASE_URL` | whapi.cloud API base URL | https://gate.whapi.cloud |
| `WEBHOOK_PORT` | Webhook server port | 8000 |
| `POLLING_INTERVAL` | Polling interval in seconds | 30 |
| `USE_WEBHOOK` | Enable webhook mode | false |

## Data Storage

The project uses **file-based state** (no database):

| File | Purpose |
|------|---------|
| `data/contacts.json` | WhatsApp contact list |
| `data/analytics.json` | Email/WhatsApp/AI post metrics |
| `data/post_history.json` | Generated AI posts history |
| `data/latest_post.json` | Latest generated post info |
| `Daily_AI_Posts/*.md` | AI-generated posts (with `.posted` marker files) |
| `logs/` | Application logs |

## Key Design Patterns

- **Subprocess-based services**: Services spawn Python scripts rather than direct imports
- **File-based state**: JSON/markdown files for persistence
- **Polling/watchdog patterns**: File system watchers and API polling for events
- **Human-in-the-loop**: Approval workflow via `Pending_Approval/` folder before execution
- **Lock file mechanism**: Prevents multiple scheduler instances

## Important Files Reference

| File | Description |
|------|-------------|
| `cammand.md` | Quick reference: which script handles which function |
| `CLAUDE.md` | Guidance for Claude Code working in this repo |
| `API_DOCS.md` | WhatsApp automation API documentation |
| `IMPLEMENTATION_SUMMARY.md` | WhatsApp system implementation details |
| `README_NICEGUI.md` | UI refactoring notes (Streamlit → NiceGUI) |

## Development Notes

- Follow PEP 8 coding standards
- Services are wrappers around standalone scripts via subprocess
- UI layer is separated from business logic
- All credentials via environment variables (never hardcoded)
- Sensitive information not logged
