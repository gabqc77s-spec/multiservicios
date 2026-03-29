import subprocess
import os
from src.agent import git_commit_changes

def audit_git_commit():
    print("--- INICIANDO AUDITORÍA REAL DE GIT COMMIT ---")

    # 1. Create a dummy change
    dummy_file = "packages/dummy_change.txt"
    os.makedirs("packages", exist_ok=True)
    with open(dummy_file, "w") as f:
        f.write("Some new content")

    print(f"Paso 1: Cambio realizado en {dummy_file}")

    # 2. Run git_commit_changes
    res = git_commit_changes()
    print(f"Paso 2: Resultado de git_commit_changes: {res}")

    if res["status"] == "success":
        # 3. Verify commit log
        log_res = subprocess.run(["git", "log", "-1", "--pretty=%B"], capture_output=True, text=True)
        print(f"Paso 3: Mensaje de commit real: {log_res.stdout.strip()}")
        assert res["message"] == log_res.stdout.strip()
        print("✅ AUDITORÍA DE GIT COMMIT EXITOSA")
    else:
        print(f"❌ AUDITORÍA DE GIT COMMIT FALLÓ: {res['message']}")

if __name__ == "__main__":
    # Ensure it's a git repo
    if not os.path.exists(".git"):
        subprocess.run(["git", "init"])
        subprocess.run(["git", "config", "user.email", "jules@agent.ai"])
        subprocess.run(["git", "config", "user.name", "Jules Agent"])
        # Initial commit
        with open("README.md", "a") as f: f.write("\n")
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", "initial commit"])

    audit_git_commit()
