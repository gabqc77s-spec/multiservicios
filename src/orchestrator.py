import subprocess
import os
import time
import signal

class ProcessManager:
    """
    Manages background processes like running microservices.
    Simulates a local orchestrator without Docker.
    """
    def __init__(self):
        self.processes = {} # pid: process_object

    def start_service(self, name, command, cwd="."):
        """
        Starts a service as a background process and keeps track of its PID.
        """
        print(f"Starting service {name}: {command}")
        try:
            # Open a log file for each process to capture output
            log_file = open(f"{name}_output.log", "w")

            process = subprocess.Popen(
                command,
                shell=True,
                cwd=cwd,
                stdout=log_file,
                stderr=log_file,
                preexec_fn=os.setsid # allows to kill process groups
            )

            self.processes[name] = {
                "process": process,
                "command": command,
                "log_file": log_file.name,
                "status": "running"
            }
            return True
        except Exception as e:
            print(f"Error starting service {name}: {e}")
            return False

    def stop_service(self, name):
        """
        Stops a running process using its PID.
        """
        if name in self.processes:
            process_data = self.processes[name]
            process = process_data["process"]
            print(f"Stopping service {name}")

            try:
                # Terminate the entire process group
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                process.wait(timeout=5)
                self.processes[name]["status"] = "stopped"
                print(f"Service {name} stopped.")
                return True
            except Exception as e:
                print(f"Error stopping service {name}: {e}")
                # Force kill if necessary
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    self.processes[name]["status"] = "terminated"
                    return True
                except:
                    return False
        return False

    def get_status(self):
        """
        Returns a dictionary of current processes and their status.
        """
        for name, data in self.processes.items():
            poll = data["process"].poll()
            if poll is not None:
                data["status"] = f"finished (exit code {poll})"
        return {name: data["status"] for name, data in self.processes.items()}

if __name__ == "__main__":
    # Test orchestrator
    manager = ProcessManager()
    manager.start_service("ping-test", "ping -c 4 127.0.0.1")
    time.sleep(2)
    print(manager.get_status())
    time.sleep(3)
    print(manager.get_status())
