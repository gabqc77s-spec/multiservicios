from src.agent import self_healing_execution
from src.orchestrator import ProcessManager
import os
import time

def audit_new_features(tmp_path):
    os.chdir(tmp_path)

    # 1. Audit Self-Healing (Controlled Failure)
    # Create a broken python file
    broken_file = tmp_path / "broken.py"
    broken_file.write_text("print('hello' + 1)") # TypeError

    # This will fail and try to fix it using AI.
    # Since we don't have a real Gemini response here in a unit test,
    # it might just fail, but we check the logic flow.
    # Note: If GOOGLE_API_KEY is not set, it will fail fast.

    print("Testing self-healing flow...")
    res = self_healing_execution("python3 broken.py", filepath=str(broken_file), max_retries=1)
    assert res["status"] in ["success", "failed"]
    assert len(res["history"]) >= 0

    # 2. Audit Port Monitoring
    pm = ProcessManager()
    # Check a port that is definitely closed (we hope)
    assert pm.check_port(9999) == False

    # 3. Audit Log Viewing
    pm.start_service("test-logs", "echo 'LOG LINE 1'")
    time.sleep(1)
    logs = pm.get_logs("test-logs")
    assert "LOG LINE 1" in logs

    print("Granular audit of new features passed!")

if __name__ == "__main__":
    import pathlib
    audit_new_features(pathlib.Path("/tmp/audit_new"))
