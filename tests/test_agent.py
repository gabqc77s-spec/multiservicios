import os
import shutil
import pytest
from src.agent import edit_file, run_command, self_healing_execution, scaffold_component

def test_edit_file(tmp_path):
    test_file = tmp_path / "subdir" / "test.txt"
    content = "hello world"
    assert edit_file(str(test_file), content) == True
    with open(test_file, "r") as f:
        assert f.read() == content

def test_run_command_allowed():
    result = run_command("echo 'test output'")
    assert result["returncode"] == 0
    assert "test output" in result["stdout"]

def test_run_command_restricted():
    # 'rm' is not in ALLOWED_COMMANDS
    result = run_command("rm -rf /")
    assert result["returncode"] == -1
    assert "Security Error" in result["stderr"]

def test_scaffold_component_mock(tmp_path):
    # Test fallback to mock when no API KEY
    if "GOOGLE_API_KEY" in os.environ:
        del os.environ["GOOGLE_API_KEY"]

    name = "mock-service"
    target_dir = tmp_path
    prompt = "A simple mock service"

    assert scaffold_component(name, str(target_dir), prompt) == True

    component_path = tmp_path / name
    assert component_path.exists()
    assert (component_path / "main.py").exists()
    assert (component_path / "README.md").exists()

def test_self_healing_placeholder():
    result = self_healing_execution("ls -l")
    assert result["returncode"] == 0
