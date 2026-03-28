import os
from src.agent import edit_file, run_command, self_healing_execution

def test_edit_file(tmp_path):
    test_file = tmp_path / "test.txt"
    content = "hello world"
    assert edit_file(str(test_file), content) == True
    with open(test_file, "r") as f:
        assert f.read() == content

def test_run_command():
    result = run_command("echo 'test output'")
    assert result["returncode"] == 0
    assert "test output" in result["stdout"]

def test_run_command_failure():
    result = run_command("non_existent_command_12345")
    assert result["returncode"] != 0
    assert result["stderr"] != ""

def test_self_healing_placeholder():
    # Placeholder should just return result if no logic provided
    result = self_healing_execution("ls -l")
    assert result["returncode"] == 0
