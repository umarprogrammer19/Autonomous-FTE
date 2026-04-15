#!/usr/bin/env python3
"""
Command Line Interface for WhatsApp Automation System
"""

import argparse
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from whatsapp_automation import WhatsAppAutomation, manual_send_message
from utils import load_env, create_sample_config


def main():
    parser = argparse.ArgumentParser(description="WhatsApp Automation System")

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Start command
    start_parser = subparsers.add_parser('start', help='Start the WhatsApp automation system')
    start_parser.add_argument('--webhook', action='store_true', help='Use webhook mode instead of polling')

    # Send command
    send_parser = subparsers.add_parser('send', help='Send a WhatsApp message')
    send_parser.add_argument('phone', help='Phone number to send message to')
    send_parser.add_argument('message', help='Message to send')

    # Config command
    config_parser = subparsers.add_parser('config', help='Configuration utilities')
    config_parser.add_argument('--create-sample', action='store_true', help='Create sample .env file')

    # Test command
    test_parser = subparsers.add_parser('test', help='Run tests')

    args = parser.parse_args()

    if args.command == 'start':
        load_env()

        # Override USE_WEBHOOK if specified
        if args.webhook:
            os.environ['USE_WEBHOOK'] = 'true'

        # Import here to avoid loading env vars too early
        from whatsapp_automation import main as automation_main
        automation_main()

    elif args.command == 'send':
        load_env()
        success = manual_send_message(args.phone, args.message)
        if success:
            print(f"Message sent successfully to {args.phone}")
        else:
            print(f"Failed to send message to {args.phone}")
            sys.exit(1)

    elif args.command == 'config':
        if args.create_sample:
            create_sample_config()
        else:
            parser.print_help()

    elif args.command == 'test':
        import subprocess
        result = subprocess.run([sys.executable, 'test_whatsapp_automation.py'])
        sys.exit(result.returncode)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()