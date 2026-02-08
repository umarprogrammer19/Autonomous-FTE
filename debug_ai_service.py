import subprocess
import sys

print("Testing subprocess call for AI scheduler...")

cmd = [sys.executable, "daily_ai_scheduler.py", "--manual"]

print(f"Command: {' '.join(cmd)}")

try:
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
        print("SUCCESS: AI post generated successfully")
    else:
        print("FAILURE: AI post generation failed")

except subprocess.TimeoutExpired:
    print("ERROR: AI post generation timed out")
except FileNotFoundError:
    print("ERROR: daily_ai_scheduler.py not found")
except Exception as e:
    print(f"UNEXPECTED ERROR: {str(e)}")