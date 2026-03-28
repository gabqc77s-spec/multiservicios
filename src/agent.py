import os
import subprocess
import shutil
from pathlib import Path

def edit_file(filepath, content):
    """
    Overwrites the file with new content.
    Optionally could use something like git stash before acting.
    """
    try:
        with open(filepath, "w") as f:
            f.write(content)
        print(f"File {filepath} updated successfully.")
        return True
    except Exception as e:
        print(f"Error editing file {filepath}: {e}")
        return False

def run_command(command, cwd="."):
    """
    Executes a shell command and returns the output and exit code.
    Used for linting, testing, and self-healing.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "returncode": -1
        }

def self_healing_execution(command, filepath=None, fix_logic=None, max_retries=3):
    """
    Runs a command (like pytest) and if it fails, attempts to heal the code.
    Requires a fix_logic function or AI guidance to fix the file.
    """
    retries = 0
    while retries < max_retries:
        print(f"Executing command: {command} (Attempt {retries + 1})")
        result = run_command(command)

        if result["returncode"] == 0:
            print("Command succeeded.")
            return result

        print(f"Command failed with error: {result['stderr']}")

        if fix_logic and filepath:
            print(f"Attempting to self-heal: {filepath}")
            # This is where an AI would be called to analyze the error and fix it.
            # For now, it's a placeholder.
            fix_logic(filepath, result["stderr"])
            retries += 1
        else:
            print("No self-healing logic provided. Returning failure.")
            return result

    return result

if __name__ == "__main__":
    # Example usage
    res = run_command("ls -l")
    print(res["stdout"])
