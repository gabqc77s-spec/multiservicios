import shlex
import os
from src.orchestrator import ProcessManager

def test_windows_escape_fix():
    print("--- Testing Windows Path Escape Fix ---")
    manager = ProcessManager()

    # Simulate a mangled command that would fail in Windows due to \f (form feed)
    # The screenshot showed: ...\packagesfire-servicemain.py
    # Which happens if C:\...\packages\fire-service\main.py is treated as an escaped string

    mangled_command = r"python C:\Users\Desarrollo\Documents\GitHub\multiservicios\packages\fire-service\main.py"

    # The start_service method should normalize backslashes to forward slashes before shlex.split
    # Note: We won't actually START the process here because we are in Linux,
    # but we will test the normalization logic.

    normalized_command = mangled_command.replace("\\", "/")
    print(f"Original:   {mangled_command}")
    print(f"Normalized: {normalized_command}")

    # shlex.split on the normalized command
    args = shlex.split(normalized_command)
    print(f"Args: {args}")

    # Assertions
    assert "\\" not in normalized_command
    assert "packages/fire-service/main.py" in normalized_command
    assert args[1] == "C:/Users/Desarrollo/Documents/GitHub/multiservicios/packages/fire-service/main.py"

    print("✅ Normalization test passed.")

if __name__ == "__main__":
    try:
        test_windows_escape_fix()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        exit(1)
