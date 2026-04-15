import subprocess
import sys
import os
import tempfile
import logging

# Enable logging to see what's happening
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

print("Testing subprocess call directly...")

try:
    # Prepare the command to run the email script with positional arguments
    cmd = [sys.executable, "daily_ai_scheduler.py", "--manual"]

    print(f"Command: {' '.join(cmd)}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python executable: {sys.executable}")

    # Execute the email script
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=60  # Longer timeout for AI generation
    )

    print(f"Return code: {result.returncode}")
    print(f"Stdout: {repr(result.stdout)}")
    print(f"Stderr: {repr(result.stderr)}")

    if result.returncode == 0:
        print("SUCCESS: Command executed successfully")
        success = True
    else:
        print("FAILURE: Command failed")
        success = False

except subprocess.TimeoutExpired:
    print("TIMEOUT: Command timed out")
    success = False
except FileNotFoundError:
    print("FILE NOT FOUND: Script not found")
    success = False
except Exception as e:
    print(f"EXCEPTION: {str(e)}")
    import traceback
    traceback.print_exc()
    success = False

print(f"Final result: {success}")