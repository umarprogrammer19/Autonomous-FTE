#!/usr/bin/env python3
"""
Test script to verify that all functionality works after UI refactoring
"""

import os
import sys
import json
from datetime import datetime


def test_services_import():
    """Test that all services can be imported"""
    print("Testing service imports...")

    try:
        from src.services.email_service import EmailService
        from src.services.whatsapp_service import WhatsAppService
        from src.services.ai_post_service import AIPostService

        print("[OK] All services imported successfully")
        return True
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False


def test_service_methods():
    """Test that all required methods exist in services"""
    print("\nTesting service methods...")

    try:
        from src.services.email_service import EmailService
        from src.services.whatsapp_service import WhatsAppService
        from src.services.ai_post_service import AIPostService

        # Check EmailService methods
        assert hasattr(
            EmailService, "send_email"
        ), "EmailService.send_email method missing"
        print("[OK] EmailService.send_email exists")

        # Check WhatsAppService methods
        assert hasattr(
            WhatsAppService, "send_message"
        ), "WhatsAppService.send_message method missing"
        print("[OK] WhatsAppService.send_message exists")

        # Check AIPostService methods
        assert hasattr(
            AIPostService, "generate_and_post_now"
        ), "AIPostService.generate_and_post_now method missing"
        assert hasattr(
            AIPostService, "get_latest_post"
        ), "AIPostService.get_latest_post method missing"
        assert hasattr(
            AIPostService, "run_scheduler_background"
        ), "AIPostService.run_scheduler_background method missing"
        print("[OK] AIPostService methods exist")

        return True
    except AssertionError as e:
        print(f"[ERROR] Method test error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Service method test error: {e}")
        return False


def test_utility_functions():
    """Test that utility functions can be imported"""
    print("\nTesting utility functions...")

    try:
        from src.utils import load_env, send_test_message, create_sample_config

        print("[OK] Utility functions imported successfully")
        return True
    except ImportError as e:
        print(f"[ERROR] Utility import error: {e}")
        return False


def test_data_functions():
    """Test the functions that handle data"""
    print("\nTesting data handling functions...")

    try:
        # Import the functions from the app
        from obsolete.app import load_contacts, save_contacts

        # Test saving and loading contacts
        test_contacts = [
            {
                "name": "Test Contact",
                "phone": "+1234567890",
                "added_date": datetime.now().isoformat(),
            }
        ]

        save_contacts(test_contacts)
        loaded_contacts = load_contacts()

        assert len(loaded_contacts) == 1, "Contact not saved/loaded properly"
        assert loaded_contacts[0]["name"] == "Test Contact", "Contact name mismatch"

        print("[OK] Data handling functions work correctly")
        return True
    except Exception as e:
        print(f"[ERROR] Data handling test error: {e}")
        return False


def test_app_structure():
    """Test that the app structure is correct"""
    print("\nTesting app structure...")

    try:
        # Import the app module and check for required elements
        import obsolete.app as app

        # Check that state object exists
        assert hasattr(app, "state"), "AppState object missing"
        print("[OK] AppState object exists")

        # Check that UI functions exist
        required_functions = [
            "dashboard_page",
            "email_sender_page",
            "whatsapp_manager_page",
            "ai_post_generator_page",
            "settings_page",
            "sidebar_navigation",
        ]

        for func_name in required_functions:
            assert hasattr(app, func_name), f"Function {func_name} missing"
            print(f"[OK] {func_name} exists")

        return True
    except Exception as e:
        print(f"[ERROR] App structure test error: {e}")
        return False


def main():
    """Run all tests"""
    print("Running functionality tests after UI refactoring...\n")

    tests = [
        test_services_import,
        test_service_methods,
        test_utility_functions,
        test_data_functions,
        test_app_structure,
    ]

    results = []
    for test_func in tests:
        results.append(test_func())

    print(f"\n{'='*50}")
    print(f"Test Results: {sum(results)}/{len(results)} passed")

    if all(results):
        print("[SUCCESS] All tests passed! The refactoring was successful.")
        return True
    else:
        print("[FAILURE] Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
