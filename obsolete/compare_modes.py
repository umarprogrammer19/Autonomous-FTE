import subprocess
import sys
import time

print("Testing auto scheduler mode (without --manual flag)...")

try:
    # Prepare the command to run the scheduler in auto mode
    cmd = [sys.executable, "daily_ai_scheduler.py"]  # No --manual flag

    print(f"Command: {' '.join(cmd)}")

    # Execute with a short timeout since auto mode runs continuously
    # We'll terminate it after a short time
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=5  # Short timeout since it runs continuously
    )

    print(f"Return code: {result.returncode}")
    print(f"Stdout: {repr(result.stdout)}")
    print(f"Stderr: {repr(result.stderr)}")

except subprocess.TimeoutExpired:
    print("Auto scheduler is running continuously (expected behavior)")
    print("This is normal for auto mode - it runs every 24 hours")
except Exception as e:
    print(f"Error in auto scheduler: {str(e)}")

print("\nNow testing manual mode...")
try:
    cmd = [sys.executable, "daily_ai_scheduler.py", "--manual"]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=60
    )

    print(f"Manual mode - Return code: {result.returncode}")
    print(f"Manual mode - Success: {result.returncode == 0}")

except Exception as e:
    print(f"Error in manual mode: {str(e)}")