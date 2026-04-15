from nicegui import ui
import os
import json
from datetime import datetime
import threading
from src.services.email_service import EmailService
from src.services.whatsapp_service import WhatsAppService
from src.services.ai_post_service import AIPostService

# Global state variables
class AppState:
    def __init__(self):
        self.scheduler_running = False
        self.last_post_time = None
        self.total_posts = 0
        self.current_page = "Dashboard"

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

def sidebar_navigation():
    """Create sidebar navigation"""
    with ui.column().classes('w-full p-4'):
        ui.label("🤖 Social Media Dashboard").classes('text-xl font-bold mb-4')

        pages = [
            "Dashboard",
            "Email Sender",
            "WhatsApp Manager",
            "AI Post Generator",
            "Settings"
        ]

        for page in pages:
            ui.button(page, on_click=lambda p=page: navigate_to_page(p)).classes('w-full mb-2')

        ui.separator().classes('my-4')

        with ui.card().classes('w-full p-4 bg-gray-100'):
            ui.label("**System Info**").classes('font-bold')
            ui.label(f"Last Post: {state.last_post_time or 'Never'}").classes('text-sm')
            ui.label(f"Total Posts: {state.total_posts}").classes('text-sm')

def navigate_to_page(page_name):
    """Navigate to a specific page"""
    state.current_page = page_name
    ui.refresh()

def dashboard_page():
    """Dashboard main page"""
    with ui.column().classes('w-full p-4'):
        ui.label("📊 Social Media Automation Dashboard").classes('text-2xl font-bold mb-6')

        # System Status Cards
        with ui.row().classes('w-full gap-4 mb-6'):
            with ui.card().classes('flex-1 p-4 bg-blue-50 border-l-4 border-blue-500'):
                ui.label("Email Service").classes('text-lg font-semibold')
                ui.label(format_status(True)).classes('text-green-600')

            with ui.card().classes('flex-1 p-4 bg-green-50 border-l-4 border-green-500'):
                ui.label("WhatsApp Service").classes('text-lg font-semibold')
                ui.label(format_status(True)).classes('text-green-600')

            with ui.card().classes('flex-1 p-4 bg-purple-50 border-l-4 border-purple-500'):
                status_text = "🟢 Running" if state.scheduler_running else "🔴 Stopped"
                ui.label("AI Scheduler").classes('text-lg font-semibold')
                ui.label(status_text).classes('text-green-600' if state.scheduler_running else 'text-red-600')

        # Scheduler Controls
        with ui.column().classes('mb-6'):
            ui.label("AI Scheduler Control").classes('text-xl font-semibold mb-4')

            with ui.row().classes('gap-4'):
                start_btn = ui.button("▶️ Start AI Scheduler", on_click=start_scheduler).classes('bg-green-500 text-white px-4 py-2 rounded')
                stop_btn = ui.button("⏹️ Stop AI Scheduler", on_click=stop_scheduler).classes('bg-red-500 text-white px-4 py-2 rounded')
                
                # Update button states based on scheduler status
                start_btn.set_enabled(not state.scheduler_running)
                stop_btn.set_enabled(state.scheduler_running)

        # Stats Section
        with ui.column().classes('mb-6'):
            ui.label("Statistics").classes('text-xl font-semibold mb-4')

            with ui.row().classes('w-full gap-4'):
                with ui.card().classes('flex-1 p-4 bg-yellow-50 border-l-4 border-yellow-500'):
                    ui.label("Last Post Time").classes('font-semibold')
                    ui.label(state.last_post_time or "Never").classes('text-lg')

                with ui.card().classes('flex-1 p-4 bg-indigo-50 border-l-4 border-indigo-500'):
                    ui.label("Total Posts Generated").classes('font-semibold')
                    ui.label(str(state.total_posts)).classes('text-lg')

        # Recent Activity
        with ui.column():
            ui.label("Recent Activity").classes('text-xl font-semibold mb-4')
            if state.last_post_time:
                ui.label(f"Latest activity: {state.last_post_time}").classes('text-lg')
            else:
                ui.label("No recent activity").classes('text-lg text-gray-500')

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
    with ui.column().classes('w-full p-4 max-w-2xl mx-auto'):
        ui.label("📧 Email Sender").classes('text-2xl font-bold mb-6')

        with ui.card().classes('w-full p-6'):
            recipient_email = ui.input("Recipient Email", placeholder="user@example.com").classes('w-full mb-4')
            subject = ui.input("Subject", placeholder="Email subject").classes('w-full mb-4')
            message = ui.textarea("Message", placeholder="Enter your message here...",
                                 rows=5).classes('w-full mb-4')

            async def send_email_handler():
                if not recipient_email.value or not subject.value or not message.value:
                    ui.notify("Please fill in all fields!", type='negative')
                    return

                try:
                    # Send email using the service
                    result = EmailService.send_email(recipient_email.value, subject.value, message.value)
                    if result:
                        ui.notify(f"✅ Email sent successfully to {recipient_email.value}!", type='positive')
                    else:
                        ui.notify("❌ Failed to send email. Please check the logs.", type='negative')
                except Exception as e:
                    ui.notify(f"❌ Error sending email: {str(e)}", type='negative')

            ui.button("📤 Send Email", on_click=send_email_handler).classes('bg-blue-500 text-white px-4 py-2 rounded')

def whatsapp_manager_page():
    """WhatsApp manager page"""
    with ui.column().classes('w-full p-4 max-w-3xl mx-auto'):
        ui.label("💬 WhatsApp Manager").classes('text-2xl font-bold mb-6')

        # Create tabs for contact management and sending
        with ui.tabs().classes('w-full') as tabs:
            contact_tab = ui.tab('Contact Management', label='Contact Management')
            send_tab = ui.tab('Send Message', label='Send Message')

        with ui.tab_panels(tabs, value=contact_tab).classes('w-full'):
            with ui.tab_panel(contact_tab):
                contact_management_section()

            with ui.tab_panel(send_tab):
                send_message_section()

def contact_management_section():
    """Contact management section"""
    with ui.column().classes('w-full'):
        ui.label("Add New Contact").classes('text-lg font-semibold mb-4')

        with ui.row().classes('w-full gap-4 mb-6'):
            name_input = ui.input("Name", placeholder="John Doe").classes('flex-1')
            phone_input = ui.input("Phone Number", placeholder="+1234567890").classes('flex-1')

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
                ui.refresh()

        ui.button("Add Contact", on_click=add_contact_handler).classes('bg-green-500 text-white px-4 py-2 rounded mb-6')

        # Display all contacts
        contacts = load_contacts()
        if contacts:
            ui.label("All Contacts").classes('text-lg font-semibold mt-6 mb-4')
            for i, contact in enumerate(contacts):
                with ui.expansion(f"{contact['name']} - {contact['phone']}", icon='person').classes('w-full mb-2'):
                    ui.label(f"Added: {contact['added_date'][:10]}")
                    ui.button(f"Delete Contact", on_click=lambda c=contact: delete_contact(c)).classes('bg-red-500 text-white px-3 py-1 rounded')

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
        ui.label("Send WhatsApp Message").classes('text-lg font-semibold mb-4')

        # Load contacts for selection
        contacts = load_contacts()

        if contacts:
            contact_names = [f"{c['name']} ({c['phone']})" for c in contacts]
            contact_select = ui.select(options=["Choose a contact..."] + contact_names,
                                      label="Select Contact").classes('w-full mb-4')

            message_area = ui.textarea("Message", placeholder="Type your message here...",
                                     rows=4).classes('w-full mb-4')

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
                        ui.notify(f"✅ Message sent to {contact_select.value}!", type='positive')
                    else:
                        ui.notify("❌ Failed to send WhatsApp message. Please check the logs.", type='negative')
                except Exception as e:
                    ui.notify(f"❌ Error sending message: {str(e)}", type='negative')

            ui.button("Send WhatsApp Message", on_click=send_whatsapp_handler).classes('bg-green-500 text-white px-4 py-2 rounded')
        else:
            ui.label("No contacts available. Please add contacts first.").classes('text-gray-500')

def ai_post_generator_page():
    """AI Post Generator page"""
    with ui.column().classes('w-full p-4 max-w-3xl mx-auto'):
        ui.label("🤖 AI Post Generator").classes('text-2xl font-bold mb-6')

        # Automatic Mode
        with ui.card().classes('w-full p-6 mb-6'):
            ui.label("Automatic Mode").classes('text-lg font-semibold mb-4')

            auto_toggle = ui.toggle([True, False], value=state.scheduler_running,
                                   on_change=lambda e: toggle_auto_post(e.value))
            ui.label("Auto Post Every 24 Hours").classes('ml-2')

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

        # Latest Post Preview
        with ui.card().classes('w-full p-6'):
            ui.label("Latest Generated Post").classes('text-lg font-semibold mb-4')
            latest_post = AIPostService.get_latest_post()
            if latest_post:
                ui.label(f"**Generated at:** {latest_post.get('timestamp', 'Unknown')}").classes('font-medium')
                ui.label(f"**Content:** {latest_post.get('content', 'No content available')}").classes('mt-2')
                ui.label(f"**Platforms:** {', '.join(latest_post.get('platforms', []))}").classes('mt-2')
            else:
                ui.label("No posts generated yet.").classes('text-gray-500')

def settings_page():
    """Settings page"""
    with ui.column().classes('w-full p-4 max-w-4xl mx-auto'):
        ui.label("⚙️ Settings").classes('text-2xl font-bold mb-6')

        ui.label("Application Settings").classes('text-xl font-semibold mb-4')

        # Log file viewer
        if os.path.exists('logs/app.log'):
            ui.label("Application Logs").classes('text-lg font-semibold mb-4')
            with open('logs/app.log', 'r') as f:
                logs = f.read()
            ui.textarea("Logs", value=logs, rows=15).classes('w-full font-mono text-sm')
        else:
            ui.label("No log file found.").classes('text-gray-500')

# Main app layout
@ui.page('/')
def main_page():
    with ui.grid(columns=12).classes('w-screen h-screen'):
        # Sidebar
        with ui.column().classes('col-span-2 bg-gray-100 min-h-screen p-4'):
            sidebar_navigation()

        # Main content
        with ui.column().classes('col-span-10 p-6 bg-white min-h-screen'):
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