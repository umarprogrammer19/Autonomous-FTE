from nicegui import ui
import os
import json
from datetime import datetime
import subprocess
import sys
import threading
import asyncio
from services.email_service import EmailService
from services.whatsapp_service import WhatsAppService
from services.ai_post_service import AIPostService
from analytics_tracker import increment_emails_sent, increment_whatsapp_sent, increment_ai_posts_generated, get_analytics

# Global state variables
class AppState:
    def __init__(self):
        self.scheduler_running = False
        self.last_post_time = None
        self.total_posts = 0
        self.current_page = "Dashboard"
        self.email_count = 0
        self.whatsapp_count = 0
        self.ai_post_count = 0

state = AppState()

def load_contacts():
    """Load contacts from JSON file"""
    if os.path.exists('data/contacts.json'):
        with open('data/contacts.json', 'r') as f:
            return json.load(f)
    return []

def save_contacts(contacts):
    """Save contacts to JSON file"""
    os.makedirs('data', exist_ok=True)
    with open('data/contacts.json', 'w') as f:
        json.dump(contacts, f, indent=2)

def format_status(status):
    """Format status with color indicator"""
    if status:
        return "🟢 Active" if status else "🔴 Inactive"
    return "⚪ Unknown"

def get_analytics_data():
    """Get analytics data from the analytics tracker"""
    analytics = get_analytics()
    
    # Update state with analytics data
    state.email_count = analytics['emails_sent']
    state.whatsapp_count = analytics['whatsapp_messages_sent']
    state.ai_post_count = analytics['ai_posts_generated']
    
    # Get last post time from the latest post
    try:
        if os.path.exists('data/post_history.json'):
            with open('data/post_history.json', 'r') as f:
                posts = json.load(f)
                if posts:
                    state.last_post_time = posts[-1]['timestamp']
    except:
        pass
        
    return {
        'emails_sent': analytics['emails_sent'],
        'whatsapp_messages': analytics['whatsapp_messages_sent'],
        'ai_posts_generated': analytics['ai_posts_generated'],
        'scheduler_status': state.scheduler_running
    }

def sidebar_navigation():
    """Create sidebar navigation"""
    with ui.column().classes('w-full p-4 bg-gray-50 min-h-screen'):
        ui.label("🤖 Social Media Dashboard").classes('text-xl font-bold mb-6 text-gray-800')

        pages = [
            ("Dashboard", "dashboard"),
            ("Email Sender", "email"),
            ("WhatsApp Manager", "whatsapp"),
            ("AI Post Generator", "ai"),
            ("Settings", "settings")
        ]

        for page_name, icon in zip(["Dashboard", "Email Sender", "WhatsApp Manager", "AI Post Generator", "Settings"], 
                                  ["dashboard", "email", "chat", "auto_awesome", "settings"]):
            with ui.row().classes('w-full items-center cursor-pointer p-3 rounded-lg hover:bg-gray-200 transition-all duration-200').on('click', lambda p=page_name: navigate_to_page(p)):
                ui.icon(icon).classes('mr-3 text-gray-600')
                ui.label(page_name).classes('text-gray-700 font-medium')
                ui.space()
                if state.current_page == page_name:
                    ui.icon('chevron_right').classes('text-blue-500')

        ui.separator().classes('my-4 bg-gray-300')

        # System status card
        with ui.card().classes('w-full p-4 bg-gradient-to-r from-blue-50 to-indigo-50 shadow-sm'):
            ui.label("System Status").classes('font-bold text-gray-700 mb-2')
            
            # Scheduler status
            status_color = 'text-green-600' if state.scheduler_running else 'text-red-600'
            status_text = "🟢 Running" if state.scheduler_running else "🔴 Stopped"
            ui.label(f"Scheduler: {status_text}").classes(f'text-sm {status_color}')
            
            # Last post time
            ui.label(f"Last Post: {state.last_post_time or 'Never'}").classes('text-sm text-gray-600')

def navigate_to_page(page_name):
    """Navigate to a specific page"""
    state.current_page = page_name
    # Update the UI by forcing a refresh of the main page
    ui.run_javascript('location.reload();')

def dashboard_page():
    """Dashboard main page"""
    analytics = get_analytics_data()
    
    with ui.column().classes('w-full p-6'):
        # Page header
        with ui.row().classes('w-full justify-between items-center mb-8'):
            ui.label("📊 Social Media AI Employee `Dashboard").classes('text-3xl font-bold text-gray-800')
            ui.button("Refresh", on_click=lambda: ui.refresh()).classes('bg-gray-200 text-gray-700 px-4 py-2 rounded-lg')

        # Analytics Cards Row
        with ui.grid(columns=4).classes('w-full gap-6 mb-8'):
            # Emails Sent Card
            with ui.card().classes('w-full p-6 bg-gradient-to-br from-blue-50 to-blue-100 shadow-md rounded-xl border-l-4 border-blue-500'):
                with ui.row().classes('items-center'):
                    ui.icon('email').classes('text-3xl text-blue-500 mr-3')
                    ui.label("Emails Sent").classes('text-lg font-semibold text-gray-700')
                ui.label(str(analytics['emails_sent'])).classes('text-3xl font-bold text-blue-600 mt-2')
                ui.label("Total emails sent successfully").classes('text-sm text-gray-600')

            # WhatsApp Messages Card
            with ui.card().classes('w-full p-6 bg-gradient-to-br from-green-50 to-green-100 shadow-md rounded-xl border-l-4 border-green-500'):
                with ui.row().classes('items-center'):
                    ui.icon('chat').classes('text-3xl text-green-500 mr-3')
                    ui.label("WhatsApp Messages").classes('text-lg font-semibold text-gray-700')
                ui.label(str(analytics['whatsapp_messages'])).classes('text-3xl font-bold text-green-600 mt-2')
                ui.label("Messages sent via WhatsApp").classes('text-sm text-gray-600')

            # AI Posts Generated Card
            with ui.card().classes('w-full p-6 bg-gradient-to-br from-purple-50 to-purple-100 shadow-md rounded-xl border-l-4 border-purple-500'):
                with ui.row().classes('items-center'):
                    ui.icon('auto_awesome').classes('text-3xl text-purple-500 mr-3')
                    ui.label("AI Posts Generated").classes('text-lg font-semibold text-gray-700')
                ui.label(str(analytics['ai_posts_generated'])).classes('text-3xl font-bold text-purple-600 mt-2')
                ui.label("Posts created by AI").classes('text-sm text-gray-600')

            # Scheduler Status Card
            with ui.card().classes('w-full p-6 bg-gradient-to-br from-indigo-50 to-indigo-100 shadow-md rounded-xl border-l-4 border-indigo-500'):
                with ui.row().classes('items-center'):
                    ui.icon('schedule').classes('text-3xl text-indigo-500 mr-3')
                    ui.label("Scheduler Status").classes('text-lg font-semibold text-gray-700')
                
                status_text = "Active" if analytics['scheduler_status'] else "Inactive"
                status_color = "text-green-600" if analytics['scheduler_status'] else "text-red-600"
                ui.label(status_text).classes(f'text-3xl font-bold {status_color} mt-2')
                ui.label("Current scheduler state").classes('text-sm text-gray-600')

        # Scheduler Controls Section
        with ui.card().classes('w-full p-6 mb-8 bg-white shadow-md rounded-xl border border-gray-200'):
            with ui.row().classes('w-full justify-between items-center'):
                ui.label("AI Scheduler Control").classes('text-2xl font-bold text-gray-800')
                
                # Status badge
                status_badge_color = "bg-green-100 text-green-800" if state.scheduler_running else "bg-red-100 text-red-800"
                status_text = "Running" if state.scheduler_running else "Stopped"
                ui.label(status_text).classes(f'px-3 py-1 rounded-full text-sm font-medium {status_badge_color}')

            with ui.row().classes('w-full gap-4 mt-4'):
                with ui.row().classes('gap-4'):
                    start_btn = ui.button("▶️ Start AI Scheduler", on_click=start_scheduler).classes('bg-gradient-to-r from-green-500 to-green-600 text-white px-6 py-3 rounded-lg font-medium shadow-md hover:shadow-lg transition-all duration-200')
                    stop_btn = ui.button("⏹️ Stop AI Scheduler", on_click=stop_scheduler).classes('bg-gradient-to-r from-red-500 to-red-600 text-white px-6 py-3 rounded-lg font-medium shadow-md hover:shadow-lg transition-all duration-200')
                    
                    # Update button states based on scheduler status
                    start_btn.set_enabled(not state.scheduler_running)
                    stop_btn.set_enabled(state.scheduler_running)

        # Recent Activity Section
        with ui.card().classes('w-full p-6 bg-white shadow-md rounded-xl border border-gray-200'):
            ui.label("Recent Activity").classes('text-2xl font-bold text-gray-800 mb-6')

            with ui.grid(columns=2).classes('w-full gap-4'):
                # Latest Post Preview
                with ui.card().classes('p-4 bg-gray-50 rounded-lg'):
                    ui.label("Latest Generated Post").classes('font-semibold text-gray-700 mb-2')
                    
                    latest_post = AIPostService.get_latest_post()
                    if latest_post:
                        ui.label(f"📝 {latest_post.get('content', 'No content available')[:100]}...").classes('text-gray-600')
                        ui.label(f"📅 {latest_post.get('timestamp', 'Unknown')}").classes('text-sm text-gray-500')
                        ui.label(f"📱 Platforms: {', '.join(latest_post.get('platforms', []))}").classes('text-sm text-gray-500')
                    else:
                        ui.label("No posts generated yet.").classes('text-gray-500 italic')

                # Activity Stats
                with ui.card().classes('p-4 bg-gray-50 rounded-lg'):
                    ui.label("Activity Summary").classes('font-semibold text-gray-700 mb-2')
                    
                    ui.label(f"🕒 Last Post: {state.last_post_time or 'Never'}").classes('text-gray-600')
                    ui.label(f"📈 Total Posts: {analytics['ai_posts_generated']}").classes('text-gray-600')
                    ui.label(f"🔔 Scheduler: {'Active' if state.scheduler_running else 'Inactive'}").classes('text-gray-600')

def start_scheduler():
    """Start the AI scheduler"""
    if not state.scheduler_running:
        state.scheduler_running = True
        # Start the scheduler in a background thread
        scheduler_thread = threading.Thread(target=AIPostService.run_scheduler_background)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        ui.notify("AI Scheduler started!", type='positive')
        ui.refresh()

def stop_scheduler():
    """Stop the AI scheduler"""
    if state.scheduler_running:
        state.scheduler_running = False
        ui.notify("AI Scheduler stopped!", type='info')
        ui.refresh()

def email_sender_page():
    """Email sender page"""
    with ui.column().classes('w-full p-6 max-w-4xl mx-auto'):
        # Page header
        ui.label("📧 Email Sender").classes('text-3xl font-bold text-gray-800 mb-8')
        
        # Description
        ui.label("Send professional emails directly from the dashboard").classes('text-gray-600 mb-8 text-lg')

        # Email form card
        with ui.card().classes('w-full p-8 bg-white shadow-xl rounded-2xl border border-gray-200'):
            with ui.column().classes('w-full'):
                recipient_email = ui.input("Recipient Email", placeholder="user@example.com").classes('w-full mb-6 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent')
                subject = ui.input("Subject", placeholder="Email subject").classes('w-full mb-6 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent')
                message = ui.textarea("Message", placeholder="Enter your message here...").classes('w-full mb-8 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent')
                message.props('rows="6"')

                async def send_email_handler():
                    if not recipient_email.value or not subject.value or not message.value:
                        ui.notify("Please fill in all fields!", type='negative')
                        return

                    try:
                        # Send email using the service
                        result = EmailService.send_email(recipient_email.value, subject.value, message.value)
                        if result:
                            increment_emails_sent()  # Track email sent
                            ui.notify(f"✅ Email sent successfully to {recipient_email.value}!", type='positive')
                            # Clear inputs after successful send
                            recipient_email.value = ""
                            subject.value = ""
                            message.value = ""
                        else:
                            ui.notify("❌ Failed to send email. Please check the logs.", type='negative')
                    except Exception as e:
                        ui.notify(f"❌ Error sending email: {str(e)}", type='negative')

        with ui.row().classes('w-full justify-center mt-6'):
            ui.button("📤 Send Email", on_click=send_email_handler).classes('bg-gradient-to-r from-blue-500 to-blue-600 text-white px-8 py-3 rounded-lg font-medium shadow-md hover:shadow-lg transition-all duration-200')

def whatsapp_manager_page():
    """WhatsApp manager page"""
    with ui.column().classes('w-full p-6 max-w-6xl mx-auto'):
        # Page header
        ui.label("💬 WhatsApp Manager").classes('text-3xl font-bold text-gray-800 mb-8')
        
        # Description
        ui.label("Manage contacts and send WhatsApp messages").classes('text-gray-600 mb-8 text-lg')

        # Create tabs for contact management and sending
        with ui.tabs().classes('w-full bg-gray-100 p-1 rounded-lg') as tabs:
            contact_tab = ui.tab('Contact Management', label='Contacts').classes('p-4 rounded-lg')
            send_tab = ui.tab('Send Message', label='Send Message').classes('p-4 rounded-lg')

        with ui.tab_panels(tabs, value=contact_tab).classes('w-full mt-4 bg-white shadow-xl rounded-2xl p-6'):
            with ui.tab_panel(contact_tab):
                contact_management_section()

            with ui.tab_panel(send_tab):
                send_message_section()

def contact_management_section():
    """Contact management section"""
    with ui.column().classes('w-full'):
        ui.label("Add New Contact").classes('text-xl font-semibold text-gray-800 mb-6')

        with ui.grid(columns=2).classes('w-full gap-6 mb-8'):
            name_input = ui.input("Name", placeholder="John Doe").classes('w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent')
            phone_input = ui.input("Phone Number", placeholder="+1234567890").classes('w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent')

        async def add_contact_handler():
            if not name_input.value or not phone_input.value:
                ui.notify("Please enter both name and phone number!", type='negative')
                return

            contacts = load_contacts()
            # Check if contact already exists
            contact_exists = any(c['phone'] == phone_input.value for c in contacts)
            if contact_exists:
                ui.notify("Contact with this phone number already exists!", type='warning')
            else:
                contacts.append({
                    "name": name_input.value,
                    "phone": phone_input.value,
                    "added_date": datetime.now().isoformat()
                })
                save_contacts(contacts)
                ui.notify(f"✅ Contact {name_input.value} added successfully!", type='positive')
                name_input.value = ""
                phone_input.value = ""
                # Refresh the page to show the new contact
                ui.run_javascript('location.reload();')

        ui.button("Add Contact", on_click=add_contact_handler).classes('bg-gradient-to-r from-green-500 to-green-600 text-white px-6 py-3 rounded-lg font-medium shadow-md hover:shadow-lg transition-all duration-200 w-fit mb-8')

        # Display all contacts
        contacts = load_contacts()
        if contacts:
            ui.label(f"All Contacts ({len(contacts)} total)").classes('text-xl font-semibold text-gray-800 mt-6 mb-6')
            
            with ui.column().classes('w-full'):
                for i, contact in enumerate(contacts):
                    with ui.card().classes('w-full p-4 bg-gray-50 rounded-lg border border-gray-200 mb-3'):
                        with ui.row().classes('w-full justify-between items-center'):
                            with ui.column():
                                ui.label(f"👤 {contact['name']}").classes('font-semibold text-gray-700')
                                ui.label(f"📞 {contact['phone']}").classes('text-gray-600 text-sm')
                                ui.label(f"📅 Added: {contact['added_date'][:10]}").classes('text-gray-500 text-xs')
                            
                            ui.button("Delete", on_click=lambda c=contact: delete_contact(c)).classes('bg-red-500 text-white px-3 py-1 rounded text-xs')
        else:
            ui.label("No contacts available. Please add contacts first.").classes('text-gray-500 text-lg')

def delete_contact(contact):
    """Delete a contact"""
    contacts = load_contacts()
    contacts.remove(contact)
    save_contacts(contacts)
    ui.notify("Contact deleted!", type='info')
    ui.refresh()

def send_message_section():
    """Send message section"""
    with ui.column().classes('w-full'):
        ui.label("Send WhatsApp Message").classes('text-xl font-semibold text-gray-800 mb-6')

        # Load contacts for selection
        contacts = load_contacts()

        if contacts:
            contact_names = [f"{c['name']} ({c['phone']})" for c in contacts]
            contact_select = ui.select(options=["Choose a contact..."] + contact_names,
                                      label="Select Contact").classes('w-full mb-6 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent')

            message_area = ui.textarea("Message", placeholder="Type your message here...").classes('w-full mb-6 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent')
            message_area.props('rows="5"')

            async def send_whatsapp_handler():
                if contact_select.value == "Choose a contact..." or not contact_select.value:
                    ui.notify("Please select a contact!", type='negative')
                    return

                if not message_area.value.strip():
                    ui.notify("Please enter a message!", type='negative')
                    return

                # Extract phone number from selected contact
                selected_index = contact_names.index(contact_select.value)
                selected_phone = contacts[selected_index]['phone']

                try:
                    # Send WhatsApp message
                    result = WhatsAppService.send_message(selected_phone, message_area.value)
                    if result:
                        increment_whatsapp_sent()  # Track WhatsApp message sent
                        ui.notify(f"✅ Message sent to {contact_select.value}!", type='positive')
                        message_area.value = ""  # Clear message after sending
                    else:
                        ui.notify("❌ Failed to send WhatsApp message. Please check the logs.", type='negative')
                except Exception as e:
                    ui.notify(f"❌ Error sending message: {str(e)}", type='negative')

        else:
            ui.label("No contacts available. Please add contacts first.").classes('text-gray-500 text-lg')
        
        # Show the send button if there are contacts
        if contacts:
            with ui.row().classes('w-full justify-center mt-6'):
                ui.button("Send WhatsApp Message", on_click=send_whatsapp_handler).classes('bg-gradient-to-r from-green-500 to-green-600 text-white px-6 py-3 rounded-lg font-medium shadow-md hover:shadow-lg transition-all duration-200')

def ai_post_generator_page():
    """AI Post Generator page"""
    with ui.column().classes('w-full p-6 max-w-4xl mx-auto'):
        # Page header
        ui.label("🤖 AI Post Generator").classes('text-3xl font-bold text-gray-800 mb-8')
        
        # Description
        ui.label("Generate and schedule social media posts with AI").classes('text-gray-600 mb-8 text-lg')

        # Auto Post Card
        with ui.card().classes('w-full p-8 mb-8 bg-gradient-to-r from-purple-50 to-indigo-50 shadow-lg rounded-2xl border border-purple-200'):
            ui.label("Automatic Posting").classes('text-xl font-semibold text-gray-800 mb-4')

            with ui.row().classes('items-center gap-4'):
                auto_toggle = ui.toggle([True, False], value=state.scheduler_running,
                                       on_change=lambda e: toggle_auto_post(e.value))
                ui.label("Enable automatic posting every 24 hours").classes('text-gray-700')
                
            ui.label("When enabled, AI will generate and post content automatically on a schedule").classes('text-gray-600 mt-2 text-sm')

        def toggle_auto_post(enabled):
            if enabled != state.scheduler_running:
                if enabled:
                    state.scheduler_running = True
                    # Start the scheduler in a background thread
                    scheduler_thread = threading.Thread(target=AIPostService.run_scheduler_background)
                    scheduler_thread.daemon = True
                    scheduler_thread.start()
                    ui.notify("Automatic posting enabled! AI will post immediately, then every 24 hours.", type='positive')
                else:
                    state.scheduler_running = False
                    ui.notify("Automatic posting disabled.", type='info')
                ui.refresh()

        # Latest Post Preview Card
        with ui.card().classes('w-full p-8 bg-white shadow-xl rounded-2xl border border-gray-200'):
            ui.label("Latest Generated Post").classes('text-xl font-semibold text-gray-800 mb-6')
            
            latest_post = AIPostService.get_latest_post()
            if latest_post:
                ui.label(f"Content:").classes('font-semibold text-gray-700')
                ui.label(f"{latest_post.get('content', 'No content available')}").classes('text-gray-600 mb-4 p-4 bg-gray-50 rounded-lg')
                
                ui.label(f"Timestamp:").classes('font-semibold text-gray-700')
                ui.label(f"{latest_post.get('timestamp', 'Unknown')}").classes('text-gray-600 mb-4')
                
                ui.label(f"Platforms:").classes('font-semibold text-gray-700')
                platforms = ', '.join(latest_post.get('platforms', []))
                ui.label(f"{platforms}").classes('text-gray-600')
                
            else:
                ui.label("No posts generated yet.").classes('text-gray-500 italic')

def settings_page():
    """Settings page"""
    with ui.column().classes('w-full p-6 max-w-6xl mx-auto'):
        # Page header
        ui.label("⚙️ Settings").classes('text-3xl font-bold text-gray-800 mb-8')
        
        # Description
        ui.label("Configure application settings and view logs").classes('text-gray-600 mb-8 text-lg')

        # Application Settings Card
        with ui.card().classes('w-full p-8 mb-8 bg-white shadow-xl rounded-2xl border border-gray-200'):
            ui.label("Application Settings").classes('text-2xl font-semibold text-gray-800 mb-6')

            # System Information
            with ui.grid(columns=2).classes('w-full gap-6 mb-8'):
                with ui.card().classes('p-4 bg-gray-50 rounded-lg'):
                    ui.label("System Information").classes('font-semibold text-gray-700 mb-3')
                    ui.label(f"Python Version: {sys.version.split()[0]}").classes('text-gray-600 text-sm')
                    import nicegui
                    ui.label(f"NiceGUI Version: {nicegui.__version__}").classes('text-gray-600 text-sm')
                    ui.label(f"Working Directory: {os.getcwd()}").classes('text-gray-600 text-sm')
                
                with ui.card().classes('p-4 bg-gray-50 rounded-lg'):
                    ui.label("Application Statistics").classes('font-semibold text-gray-700 mb-3')
                    analytics = get_analytics_data()
                    ui.label(f"Emails Sent: {analytics['emails_sent']}").classes('text-gray-600 text-sm')
                    ui.label(f"WhatsApp Messages: {analytics['whatsapp_messages']}").classes('text-gray-600 text-sm')
                    ui.label(f"AI Posts Generated: {analytics['ai_posts_generated']}").classes('text-gray-600 text-sm')

        # Log Viewer Card
        with ui.card().classes('w-full p-8 bg-gray-900 text-gray-100 rounded-2xl shadow-xl'):
            ui.label("Application Logs").classes('text-2xl font-semibold text-white mb-6')
            
            if os.path.exists('logs/app.log'):
                with open('logs/app.log', 'r') as f:
                    logs = f.read()
                log_textarea = ui.textarea("Logs", value=logs).classes('w-full font-mono text-sm bg-gray-800 text-green-400 border border-gray-700')
                log_textarea.props('rows="15"')
            else:
                ui.label("No log file found.").classes('text-gray-400')

# Main app layout
@ui.page('/')
def main_page():
    with ui.grid(columns=12).classes('w-screen h-screen bg-gray-100'):
        # Sidebar
        with ui.column().classes('col-span-2 bg-white shadow-lg min-h-screen p-4 border-r border-gray-200'):
            sidebar_navigation()

        # Main content
        with ui.column().classes('col-span-10 p-0 min-h-screen overflow-y-auto'):
            if state.current_page == "Dashboard":
                dashboard_page()
            elif state.current_page == "Email Sender":
                email_sender_page()
            elif state.current_page == "WhatsApp Manager":
                whatsapp_manager_page()
            elif state.current_page == "AI Post Generator":
                ai_post_generator_page()
            elif state.current_page == "Settings":
                settings_page()

# Run the app
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Social Media Automation Dashboard", port=8080, reload=False)