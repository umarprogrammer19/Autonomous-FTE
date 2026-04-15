import subprocess
import sys

print("Testing subprocess call as the service would...")
cmd = [
    sys.executable,  # Use the same Python interpreter
    "email_mcp_server.py",
    "test@example.com",
    "Test Subject from Service",
    "Test Message from Service"
]

print(f"Command: {' '.join(cmd)}")

try:
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30  # Timeout after 30 seconds
    )

    print(f"Return code: {result.returncode}")
    print(f"Stdout: {repr(result.stdout)}")
    print(f"Stderr: {repr(result.stderr)}")

    if result.returncode == 0:
        print("SUCCESS: Email sent successfully")
    else:
        print("FAILURE: Email sending failed")

except subprocess.TimeoutExpired:
    print("ERROR: Email sending timed out")
except FileNotFoundError:
    print("ERROR: email_mcp_server.py not found")
except Exception as e:
    print(f"UNEXPECTED ERROR: {str(e)}")