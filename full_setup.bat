@echo off
echo Configuring AI Employee Silver Tier System...

echo Setting up environment variables...
setx EMAIL_ADDRESS "meoahsan01@gmail.com"
setx EMAIL_APP_PASSWORD "oyty odzb kycj fhaa"
setx SMTP_SERVER "smtp.gmail.com"
setx SMTP_PORT "587"

echo Installing required Python packages...
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client playwright schedule

echo Installing Playwright browsers...
playwright install chromium

echo Setup complete!
echo Please ensure you have placed your gmail_credentials.json file in the AI_Employee_Vault directory.
echo Run 'python orchestrator.py' to start the system.
echo Run 'npx @playwright/mcp@latest' separately to start the Playwright MCP server.

pause