from src.orchestrator import ProcessManager
import time
import os

def test_orchestrator_granular(tmp_path):
    os.chdir(tmp_path)
    pm = ProcessManager()

    # 1. Start a long running process
    # Using 'sleep' as it's common
    pm.start_service("sleepy", "sleep 10")
    status = pm.get_status()
    assert status["sleepy"] == "running"

    # 2. Verify log file creation
    assert os.path.exists("sleepy_output.log")

    # 3. Stop process
    pm.stop_service("sleepy")
    status = pm.get_status()
    assert "stopped" in status["sleepy"] or "finished" in status["sleepy"]

    # 4. Start a failing process
    pm.start_service("fail", "ls /non-existent-path")
    time.sleep(1) # Give it time to fail
    status = pm.get_status()
    assert "finished" in status["fail"]

    # Verify log captures error
    with open("fail_output.log", "r") as f:
        log = f.read()
        assert "No such file or directory" in log

    print("Orchestrator granular audit passed!")

if __name__ == "__main__":
    import pathlib
    test_orchestrator_granular(pathlib.Path("/tmp/orchestrator_test"))
