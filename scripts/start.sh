#!/bin/bash

# Startup script for WhatsApp Automation System

echo "Starting WhatsApp Automation System..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed or not in PATH"
    exit 1
fi

# Check if requirements are installed
if ! python3 -c "import requests" &> /dev/null; then
    echo "Installing requirements..."
    pip3 install -r requirements.txt
fi

# Run the WhatsApp automation system
python3 whatsapp_automation.py