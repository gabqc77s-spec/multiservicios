import time
import os
from src.orchestrator import ProcessManager

def test_start_and_stop_service():
    manager = ProcessManager()
    service_name = "test-sleep"
    # use sleep since it's a long running process
    assert manager.start_service(service_name, "sleep 10") == True

    status = manager.get_status()
    assert service_name in status
    assert status[service_name] == "running"

    # Cleanup log file
    log_file = f"{service_name}_output.log"

    assert manager.stop_service(service_name) == True
    status = manager.get_status()
    # It can be 'stopped' or 'finished (exit code -15)' depending on timing
    assert "stopped" in status[service_name] or "finished" in status[service_name]

    if os.path.exists(log_file):
        os.remove(log_file)

def test_service_exit_code():
    manager = ProcessManager()
    service_name = "test-exit"
    # Command that exits immediately
    assert manager.start_service(service_name, "echo 'hello'") == True
    time.sleep(1) # wait for process to finish

    status = manager.get_status()
    assert "finished" in status[service_name]

    # Cleanup
    log_file = f"{service_name}_output.log"
    if os.path.exists(log_file):
        os.remove(log_file)
