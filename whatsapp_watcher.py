import asyncio
import os
import time
from playwright.async_api import async_playwright
from datetime import datetime
import json
import re

class WhatsAppWatcher:
    """
    WhatsApp Watcher script using Playwright to monitor WhatsApp Web for specific keywords
    and create .md files in Needs_Action folder when triggered.
    """

    def __init__(self, vault_path="C:/Users/AHSEN/Desktop/hackathon_0/AI_Employee_Vault", keywords=None):
        self.vault_path = vault_path
        self.needs_action_path = os.path.join(vault_path, "Needs_Action")
        self.keywords = keywords or ["urgent", "asap", "important", "meeting", "deadline"]
        self.browser = None
        self.page = None
        self.last_message_check = {}

    async def setup_browser(self):
        """Setup Playwright browser instance"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)  # Keep visible for user to scan QR
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()

        # Navigate to WhatsApp Web
        await self.page.goto('https://web.whatsapp.com')
        print("Please scan the QR code to log in to WhatsApp Web...")

        # Wait for user to log in (check for chat list)
        await self.page.wait_for_selector('div[data-testid="chat-list"]', timeout=60000)
        print("Successfully logged in to WhatsApp Web")

    async def get_chat_messages(self, chat_selector):
        """Get messages from a specific chat"""
        try:
            # Click on the chat to open it
            await self.page.click(chat_selector)
            await asyncio.sleep(2)  # Wait for chat to load

            # Get all messages
            message_elements = await self.page.query_selector_all('div.copyable-text span[dir="ltr"]')
            messages = []

            for element in message_elements:
                text = await element.inner_text()
                messages.append(text)

            return messages
        except Exception as e:
            print(f"Error getting messages from chat: {e}")
            return []

    async def monitor_chats(self):
        """Monitor all chats for keywords"""
        try:
            # Get all chat elements
            chat_elements = await self.page.query_selector_all('div[data-testid="chat-list"] div[tabindex="0"]')

            for i, chat_element in enumerate(chat_elements):
                try:
                    # Get chat name/title
                    title_element = await chat_element.query_selector('div[data-testid="cell-frame-title"] span')
                    if title_element:
                        chat_title = await title_element.inner_text()
                    else:
                        # Alternative selector for chat title
                        title_element = await chat_element.query_selector('._19vo_ div:nth-child(1)')
                        if title_element:
                            chat_title = await title_element.inner_text()
                        else:
                            chat_title = f"Chat {i}"

                    # Get the last message preview
                    last_msg_element = await chat_element.query_selector('div[data-testid="conversation-snippet"] span')
                    if last_msg_element:
                        last_message = await last_msg_element.inner_text()
                    else:
                        # Alternative selector for last message
                        last_msg_element = await chat_element.query_selector('._19vo_ div:nth-child(2) span')
                        if last_msg_element:
                            last_message = await last_msg_element.inner_text()
                        else:
                            last_message = ""

                    # Check if we've seen this message before
                    chat_key = f"{chat_title}_{last_message[:50]}"  # Use first 50 chars as key

                    if chat_key in self.last_message_check:
                        continue  # Already processed this message

                    # Check for keywords in the last message
                    found_keywords = []
                    for keyword in self.keywords:
                        if re.search(r'\b' + re.escape(keyword) + r'\b', last_message, re.IGNORECASE):
                            found_keywords.append(keyword)

                    if found_keywords:
                        print(f"Keyword(s) '{', '.join(found_keywords)}' found in chat '{chat_title}': {last_message}")
                        await self.create_action_item(chat_title, last_message, found_keywords)

                        # Remember this message to avoid duplicate processing
                        self.last_message_check[chat_key] = time.time()

                except Exception as e:
                    print(f"Error processing chat: {e}")
                    continue

        except Exception as e:
            print(f"Error monitoring chats: {e}")

    async def create_action_item(self, chat_title, message, keywords):
        """Create a markdown file in Needs_Action folder"""
        filename = f"whatsapp_{chat_title.replace(' ', '_')}_{int(time.time())}.md"
        filepath = os.path.join(self.needs_action_path, filename)

        # Sanitize filename to remove invalid characters
        filepath = "".join(c for c in filepath if c not in '<>:"/\\|?*')

        # Create markdown content
        md_content = f"""# WhatsApp Notification: {chat_title}

## Message Details
- **Chat:** {chat_title}
- **Keywords Detected:** {', '.join(keywords)}
- **Message:** {message}

## Action Required
- [ ] Review WhatsApp message
- [ ] Determine appropriate response
- [ ] Respond to contact if needed
- [ ] Take necessary follow-up action
- [ ] Update status to completed

## Response Options
1. Respond directly via WhatsApp
2. Schedule a call/meeting
3. Forward to team member
4. Archive if not actionable

---
*Created by WhatsApp Watcher on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        # Write the markdown file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"Created action item: {filepath}")

    async def run(self):
        """Main function to run the WhatsApp watcher"""
        print("Setting up WhatsApp Watcher...")

        # Create Needs_Action directory if it doesn't exist
        os.makedirs(self.needs_action_path, exist_ok=True)

        try:
            await self.setup_browser()
            print("WhatsApp Watcher started successfully!")

            while True:
                try:
                    await self.monitor_chats()
                    print("Waiting 60 seconds before next check...")
                    await asyncio.sleep(60)  # Wait 1 minute before next check
                except KeyboardInterrupt:
                    print("WhatsApp Watcher stopped by user")
                    break
                except Exception as e:
                    print(f"Error in WhatsApp Watcher: {e}")
                    await asyncio.sleep(10)  # Wait 10 seconds before retrying

        except Exception as e:
            print(f"Failed to setup WhatsApp Watcher: {e}")
        finally:
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()

if __name__ == "__main__":
    # Run the WhatsApp watcher
    async def main():
        watcher = WhatsAppWatcher()
        await watcher.run()

    asyncio.run(main())