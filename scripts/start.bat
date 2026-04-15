@echo off
REM Startup script for WhatsApp Automation System

echo Starting WhatsApp Automation System...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if requirements are installed
pip list | findstr -i -c:"requests" >nul
if errorlevel 1 (
    echo Installing requirements...
    pip install -r requirements.txt
)

REM Run the WhatsApp automation system
python whatsapp_automation.py

pause