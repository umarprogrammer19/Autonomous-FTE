# Social Media Automation Dashboard

A comprehensive social media automation platform built with NiceGUI that enables users to manage email campaigns, WhatsApp messaging, and AI-powered social media content generation through an intuitive web interface.

## Project Overview

This project is a social media automation dashboard that combines multiple communication channels into a single, easy-to-use interface. It features AI-powered content generation, automated scheduling, and analytics tracking to help users manage their social media presence efficiently.

## Features

- **Dashboard Interface**: Real-time analytics and system status monitoring
- **Email Campaign Management**: Send professional emails directly from the dashboard
- **WhatsApp Messaging**: Manage contacts and send WhatsApp messages programmatically
- **AI Post Generation**: Automatically generate social media content using AI
- **Automated Scheduling**: Schedule posts to be published every 24 hours
- **Analytics Tracking**: Monitor email sends, WhatsApp messages, and AI posts generated
- **Contact Management**: Store and manage contact information for outreach
- **Log Monitoring**: View application logs directly in the interface

## Project Architecture

### Folder Structure
```
├── app_nicegui_enhanced.py          # Main application file with UI components
├── services/
│   ├── email_service.py             # Email sending functionality
│   ├── whatsapp_service.py          # WhatsApp messaging functionality
│   └── ai_post_service.py           # AI post generation and scheduling
├── daily_ai_scheduler.py            # Background scheduler for AI posts
├── social_poster.py                 # Social media posting functionality
├── analytics_tracker.py             # Analytics and metrics tracking
├── data/                            # Runtime data storage (contacts, posts, analytics)
├── logs/                            # Application logs
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variable template
└── README.md                        # Project documentation
```

### Key Components

#### Main Application (`app_nicegui_enhanced.py`)
- **State Management**: Uses `AppState` class to maintain global application state
- **Navigation**: Sidebar navigation with Dashboard, Email Sender, WhatsApp Manager, AI Post Generator, and Settings
- **UI Framework**: Built with NiceGUI for responsive web interface
- **Analytics Integration**: Real-time display of email, WhatsApp, and AI post metrics

#### Services Layer
- **Email Service**: Handles email delivery using external scripts
- **WhatsApp Service**: Manages WhatsApp message sending via API
- **AI Post Service**: Coordinates AI-generated content creation and scheduling

#### Schedulers
- **Daily AI Scheduler**: Runs every 24 hours to generate and post AI content
- **Social Poster**: Monitors generated content and posts to social platforms

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Step-by-Step Setup

1. **Clone or download the repository**
   ```bash
   git clone <repository-url>
   cd hackathon_0_complete
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   - Copy `.env.example` to `.env`:
     ```bash
     copy .env.example .env  # On Windows
     # or
     cp .env.example .env    # On macOS/Linux
     ```
   - Update the values in `.env` with your actual API credentials

6. **Create necessary directories**
   ```bash
   mkdir data logs
   ```

## Running the Application

1. **Start the application**
   ```bash
   python app_nicegui_enhanced.py
   ```

2. **Access the dashboard**
   - Open your web browser
   - Navigate to `http://localhost:8080`
   - The dashboard will be available with all features

3. **Stopping the application**
   - Press `Ctrl+C` in the terminal where the application is running

## Optional Enhancements

### Screenshots
The application features a modern, responsive UI with:
- Dashboard showing real-time analytics
- Email composition interface
- WhatsApp contact management
- AI post generation controls
- System settings and logs viewer

### Usage Examples

#### Sending an Email
1. Navigate to "Email Sender" in the sidebar
2. Fill in recipient email, subject, and message
3. Click "Send Email" button

#### Managing WhatsApp Contacts
1. Go to "WhatsApp Manager"
2. Use "Contact Management" tab to add new contacts
3. Switch to "Send Message" tab to send messages to stored contacts

#### Generating AI Posts
1. Visit "AI Post Generator" page
2. Toggle "Enable automatic posting every 24 hours" to start the scheduler
3. View the latest generated post in the preview section

### Customization Notes

- **Themes**: The UI uses a clean, modern design with gradient cards and intuitive navigation
- **Analytics**: Metrics are stored in JSON files in the `data/` directory
- **Logging**: All activities are logged to `logs/app.log` for debugging
- **Scheduling**: The AI scheduler runs every 24 hours by default but can be modified in `daily_ai_scheduler.py`

## Contributing

We welcome contributions to improve this project! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add some amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 coding standards
- Write clear, descriptive commit messages
- Add comments for complex logic
- Maintain backward compatibility when possible
- Update documentation as needed

### Areas for Improvement
- Add more social media platform integrations
- Implement advanced scheduling options
- Enhance the AI content generation algorithms
- Add more comprehensive analytics and reporting
- Improve error handling and user notifications

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Built with ❤️ using [NiceGUI](https://nicegui.io/)