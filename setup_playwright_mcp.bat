@echo off
echo Setting up Playwright MCP Server...

:: Install Playwright if not already installed
pip install playwright

:: Install browsers for Playwright
playwright install chromium

:: Install the Playwright MCP server
npx @playwright/mcp@latest

echo Playwright MCP Server setup complete!
echo Please run "npx @playwright/mcp@latest" to start the server when needed.
pause