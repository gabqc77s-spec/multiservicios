import subprocess
import os
import time
import signal
import sys
import shlex
import socket
import re
from pathlib import Path
try:
    from .utils import clean_command, normalize_path
except ImportError:
    from utils import clean_command, normalize_path

class ProcessManager:
    """
    Manages background processes like running microservices.
    Simulates a local orchestrator without Docker.
    """
    def __init__(self):
        self.processes = {} # pid: process_object

    def pre_check_service(self, name, command, cwd="."):
        """
        Performs a health check before starting a service.
        Checks for port availability and missing dependencies.
        """
        results = {"status": "ok", "warnings": [], "errors": []}

        # 1. Port Check
        ports = self.detect_ports(command)
        for p in ports:
            if self.check_port(p):
                results["status"] = "error"
                results["errors"].append(f"Port {p} is already in use.")

        # 2. Dependency Check (Simplified)
        req_path = Path(cwd) / "requirements.txt"
        if req_path.exists():
            # Very basic check: see if a .venv exists or if we can run a check
            # In a real scenario, we might use 'pip check' or parse requirements.txt
            pass

        return results

    def start_service(self, name, command, cwd="."):
        """
        Starts a service as a background process and keeps track of its PID.
        Safe execution without shell=True.
        Automatically detects and uses local .venv if present.
        """
        # Normalize command to use / instead of \ to prevent escape issues in Windows
        command = clean_command(command)
        print(f"Starting service {name}: {command}")

        try:
            # Split command safely
            args = shlex.split(command)
            if not args:
                return False

            # Isolated Venv Support:
            # If the command starts with 'python' or 'python3', and there's a .venv in cwd
            if args[0] in ["python", "python3"]:
                venv_python = Path(cwd) / ".venv" / ("Scripts" if sys.platform == "win32" else "bin") / ("python.exe" if sys.platform == "win32" else "python")
                if venv_python.exists():
                    print(f"Using local virtual environment: {venv_python}")
                    args[0] = normalize_path(venv_python)
            if not args:
                return False

            # Open a log file for each process to capture output
            log_file = open(f"{name}_output.log", "w")

            # Cross-platform process group creation
            kwargs = {}
            if sys.platform != 'win32':
                kwargs.update(preexec_fn=os.setsid)
            else:
                kwargs.update(creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)

            process = subprocess.Popen(
                args,
                shell=False,
                cwd=cwd,
                stdout=log_file,
                stderr=log_file,
                **kwargs
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

    def stop_all(self):
        """
        Stops all running services.
        """
        names = list(self.processes.keys())
        for name in names:
            self.stop_service(name)
        return True

    def start_all(self, services_config):
        """
        Starts multiple services from a configuration dictionary {name: command}.
        """
        results = {}
        for name, cmd in services_config.items():
            results[name] = self.start_service(name, cmd)
        return results

    def stop_service(self, name):
        """
        Stops a running process using its PID.
        """
        if name in self.processes:
            process_data = self.processes[name]
            process = process_data["process"]
            print(f"Stopping service {name}")

            try:
                if sys.platform != 'win32':
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                else:
                    os.kill(process.pid, signal.CTRL_BREAK_EVENT)

                process.wait(timeout=5)
                self.processes[name]["status"] = "stopped"
                print(f"Service {name} stopped.")
                return True
            except Exception as e:
                print(f"Error stopping service {name}: {e}")
                # Force kill
                try:
                    process.kill()
                    self.processes[name]["status"] = "terminated"
                    return True
                except:
                    return False
        return False

    def check_port(self, port):
        """
        Checks if a local port is currently in use.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                return s.connect_ex(('127.0.0.1', int(port))) == 0
        except:
            return False

    def detect_ports(self, command):
        """
        Uses Regex to find potential port numbers in a command string.
        """
        # Look for patterns like :8000, port 8000, -p 8000, --port 8000, 0.0.0.0:8000, PORT=5000
        patterns = [
            r':(\d{4,5})',
            r'port\s+(\d{4,5})',
            r'-p\s+(\d{4,5})',
            r'--port\s+(\d{4,5})',
            r'\d+\.\d+\.\d+\.\d+:(\d{4,5})',
            r'PORT=(\d{4,5})'
        ]
        ports = set()
        for p in patterns:
            found = re.findall(p, command)
            for f in found:
                ports.add(int(f))

        # Also look for standalone numbers at the end of common server commands
        if not ports:
            standalone = re.search(r'\s+(\d{4,5})$', command)
            if standalone:
                ports.add(int(standalone.group(1)))

        return list(ports)

    def get_logs(self, name, tail=50):
        """
        Reads the last N lines from a service's log file.
        """
        if name in self.processes:
            log_path = self.processes[name]["log_file"]
            if os.path.exists(log_path):
                with open(log_path, "r") as f:
                    lines = f.readlines()
                    return "".join(lines[-tail:])
        return "Logs not found."

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
    # Use a safe command for testing
    manager.start_service("test-service", "ls -la")
    time.sleep(2)
    print(manager.get_status())
    time.sleep(3)
    print(manager.get_status())
