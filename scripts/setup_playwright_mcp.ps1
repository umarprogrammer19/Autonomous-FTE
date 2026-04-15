Write-Host "Setting up Playwright MCP Server..." -ForegroundColor Green

# Install Playwright if not already installed
Write-Host "Installing Playwright..."
pip install playwright

# Install browsers for Playwright
Write-Host "Installing Playwright browsers..."
playwright install chromium

# Install the Playwright MCP server
Write-Host "Installing Playwright MCP server..."
npx @playwright/mcp@latest

Write-Host "Playwright MCP Server setup complete!" -ForegroundColor Green
Write-Host "Please run 'npx @playwright/mcp@latest' to start the server when needed."