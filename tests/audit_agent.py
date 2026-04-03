from src.agent import is_safe_path, edit_file, run_command
import os

def test_agent_granular_security(tmp_path):
    # 1. Test path traversal with '..'
    base = tmp_path / "app"
    base.mkdir()

    # Target outside base
    outside = tmp_path / "outside.txt"
    outside.write_text("secret")

    # is_safe_path should return False for relative escape
    assert is_safe_path(str(base / "../outside.txt"), base_dir=str(base)) == False

    # 2. Test edit_file with unsafe path
    assert edit_file(str(tmp_path / "secret.txt"), "hacked", base_dir=str(base)) == False

    # 3. Test run_command with multiple commands (injection attempt)
    # Even if ALLOWED_COMMANDS is "echo", someone might try "echo hello; rm -rf /"
    # Since we use shell=False, the whole string is treated as arguments to the first command
    # but shlex.split will split them.

    res = run_command("echo hello; ls")
    # shlex.split("echo hello; ls") -> ["echo", "hello;", "ls"]
    # This might actually run 'echo' with args 'hello;' and 'ls'
    assert res["returncode"] == 0
    assert "hello; ls" in res["stdout"] # Verify it didn't actually execute 'ls' separately

    # 4. Test unauthorized command
    res = run_command("cat /etc/passwd")
    assert "Security Error" in res["stderr"]

    print("Agent granular security audit passed!")

if __name__ == "__main__":
    import pathlib
    test_agent_granular_security(pathlib.Path("/tmp/agent_test"))
