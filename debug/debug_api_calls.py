"""
Debug script to test the actual API calls to whapi.cloud
"""
import os
import requests
import json
from src.whatsapp_automation import WhatsAppAutomation

def debug_api_calls():
    """Debug the actual API calls being made"""
    print("[DEBUG] Debugging whapi.cloud API Calls")
    print("=" * 50)

    # Create instance (make sure token is set properly)
    try:
        wa = WhatsAppAutomation()
    except ValueError as e:
        print(f"[ERROR] Error initializing: {e}")
        print("   Please make sure your .env file has a valid WHAPI_TOKEN")
        return

    print("[SUCCESS] WhatsAppAutomation initialized successfully")

    # Test the headers
    print(f"[INFO] Headers prepared: {list(wa.headers.keys())}")

    # Manually test the API call
    url = f"{wa.api_url_base}/messages"
    params = {
        'limit': 50,
        'direction': 'incoming',
        'view': 'simple',
    }

    print(f"[REQUEST] Making request to: {url}")
    print(f"[PARAMS] Parameters: {params}")

    try:
        response = requests.get(url, headers=wa.headers, params=params, timeout=15)

        print(f"[RESPONSE] Status: {response.status_code}")
        print(f"[HEADERS] Response Headers: {dict(response.headers)}")

        try:
            response_data = response.json()
            print(f"[DATA] Response Data Keys: {list(response_data.keys()) if isinstance(response_data, dict) else type(response_data)}")
            print(f"[RAW] Raw Response Preview: {str(response.text)[:500]}...")
        except:
            print(f"[RAW] Raw Response: {response.text[:500]}...")

    except requests.exceptions.Timeout:
        print("[TIMEOUT] Request timed out - check your network connection")
    except requests.exceptions.RequestException as e:
        print(f"[FAIL] Request failed: {e}")
    except Exception as e:
        print(f"[CRASH] Unexpected error: {e}")

def check_token_status():
    """Check if the token is properly set"""
    token = os.getenv('WHAPI_TOKEN', 'not_set')
    print(f"[KEY] Current token status: {'SET' if token and token != 'your_actual_whapi_cloud_token_here' else 'NOT SET PROPERLY'}")
    if token == 'your_actual_whapi_cloud_token_here':
        print("[WARN] Token is still the placeholder - please update your .env file")

if __name__ == "__main__":
    check_token_status()
    print()
    debug_api_calls()