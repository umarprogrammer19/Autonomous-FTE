#!/usr/bin/env python3
"""
Setup script for WhatsApp Automation System
"""

import os
import sys
from pathlib import Path


def create_directories():
    """Create necessary directories"""
    dirs_to_create = []

    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(exist_ok=True)
        print(f"Created directory: {dir_path}")


def create_sample_files():
    """Create sample configuration files if they don't exist"""
    env_file = Path(".env")
    if not env_file.exists():
        env_example = Path(".env.example")
        if env_example.exists():
            env_file.write_text(env_example.read_text())
            print("Created .env file from .env.example")
        else:
            print("Warning: .env.example not found")


def install_dependencies():
    """Install required Python packages"""
    import subprocess

    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("Error installing dependencies")
        return False

    return True


def verify_environment():
    """Verify that environment is properly set up"""
    required_vars = ["WHAPI_TOKEN"]
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"Warning: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file")
        return False

    return True


def main():
    """Main setup function"""
    print("Setting up WhatsApp Automation System...")

    create_directories()
    create_sample_files()

    print("\nInstalling dependencies...")
    if install_dependencies():
        print("✓ Dependencies installed")
    else:
        print("✗ Failed to install dependencies")
        return 1

    print("\nVerifying environment...")
    if verify_environment():
        print("✓ Environment verified")
    else:
        print("⚠ Environment verification incomplete - please check warnings above")

    print("\nSetup complete!")
    print("\nTo start the WhatsApp Automation:")
    print("  python whatsapp_automation.py")
    print("\nTo send a test message:")
    print("  python -c \"from utils import send_test_message; send_test_message('PHONE_NUMBER', 'MESSAGE')\"")

    return 0


if __name__ == "__main__":
    sys.exit(main())