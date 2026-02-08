"""
Test script to verify whapi.cloud API connectivity
"""

import os
import requests

def test_api_connectivity():
    """Test basic connectivity to whapi.cloud API"""

    # Load the token
    token = os.getenv('WHAPI_TOKEN', 'your_actual_whapi_cloud_token_here')
    api_url_base = os.getenv('WHAPI_BASE_URL', 'https://gate.whapi.cloud')

    if token == 'your_actual_whapi_cloud_token_here':
        print("[ERROR] WHAPI_TOKEN not set in environment. Please update your .env file.")
        return False

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {token}"
    }

    # Test basic connectivity with a simple API call
    try:
        # Try to get account info or health check
        url = f"{api_url_base}/account"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code in [200, 201]:
            print("[SUCCESS] Successfully connected to whapi.cloud API")
            print(f"   Response: {response.status_code}")
            return True
        elif response.status_code == 401:
            print("[ERROR] Invalid token - Unauthorized (401)")
            print("   Please verify your WHAPI_TOKEN is correct")
            return False
        elif response.status_code == 403:
            print("[ERROR] Access forbidden (403)")
            print("   Please check your account permissions")
            return False
        elif response.status_code == 404:
            print("[WARNING] Account endpoint not found, trying alternative endpoints...")
        else:
            print(f"[ERROR] API returned unexpected status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("[ERROR] Connection error - unable to reach whapi.cloud")
        return False
    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out - check your network connection")
        return False
    except Exception as e:
        print(f"[ERROR] Error connecting to API: {str(e)}")
        return False

    # If account endpoint didn't work, try other common endpoints
    endpoints_to_try = [
        f"{api_url_base}/health",
        f"{api_url_base}/info",
        f"{api_url_base}/channels",
        f"{api_url_base}/chats"
    ]

    for endpoint in endpoints_to_try:
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            if response.status_code in [200, 201]:
                print(f"[SUCCESS] Successfully connected to whapi.cloud API via {endpoint}")
                return True
            elif response.status_code in [401, 403]:
                print(f"[ERROR] Invalid token or insufficient permissions for {endpoint}")
                return False
        except:
            continue

    print("[ERROR] Unable to connect to any whapi.cloud endpoints")
    print("   Please verify:")
    print("   - Your WHAPI_TOKEN is correct")
    print("   - Your WhatsApp Business account is properly connected to whapi.cloud")
    print("   - You have the necessary permissions")
    return False

def main():
    print("Testing whapi.cloud API Connectivity")
    print("=" * 40)

    success = test_api_connectivity()

    if success:
        print("\n[SUCCESS] API connectivity test PASSED")
        print("You can now run the WhatsApp automation system")
    else:
        print("\n[FAILED] API connectivity test FAILED")
        print("Please fix the issues above before running the system")

if __name__ == "__main__":
    main()