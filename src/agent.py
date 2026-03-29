import os
import subprocess
import shutil
import json
import shlex
from pathlib import Path, PurePath
from llama_index.llms.google_genai import GoogleGenAI

# Restricted list of allowed base commands for security
ALLOWED_COMMANDS = ["ls", "pytest", "python", "python3", "npm", "yarn", "pip", "git", "echo"]

def is_safe_path(path, base_dir=None):
    """
    Validates that the path is within the base_dir (defaults to current working directory)
    and does not attempt to escape it using '..'.
    """
    if base_dir is None:
        base_dir = os.getcwd()

    try:
        base_path = Path(base_dir).resolve()
        target_path = Path(path).resolve()

        # Allow paths in /tmp for testing, but still check for traversal within /tmp if base_dir is /tmp subfolder
        if str(target_path).startswith("/tmp/") and base_dir is None:
            return True

        return base_path in target_path.parents or base_path == target_path
    except Exception:
        return False

def edit_file(filepath, content):
    """
    Overwrites the file with new content.
    """
    if not is_safe_path(filepath):
        print(f"Security Error: Attempted to edit file outside of allowed directory: {filepath}")
        return False

    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"File {filepath} updated successfully.")
        return True
    except Exception as e:
        print(f"Error editing file {filepath}: {e}")
        return False

def run_command(command, cwd="."):
    """
    Executes a shell command safely without shell=True.
    Includes base command validation.
    """
    if not command:
        return {"stdout": "", "stderr": "No command provided", "returncode": -1}

    try:
        # En Windows, shlex.split puede comerse las barras invertidas si no se escapan.
        # Normalizamos a barras normales para evitar errores de ruta.
        command = command.replace("\\", "/")

        # Split command into a list of arguments safely
        args = shlex.split(command)
        if not args:
             return {"stdout": "", "stderr": "Invalid command", "returncode": -1}

        base_cmd = args[0]
        if base_cmd not in ALLOWED_COMMANDS:
            return {
                "stdout": "",
                "stderr": f"Security Error: Command '{base_cmd}' is not in the allowed list: {ALLOWED_COMMANDS}",
                "returncode": -1
            }

        # Execute without shell=True to prevent command injection
        result = subprocess.run(
            args,
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

def ai_edit_file(filepath, instruction):
    """
    Uses Gemini LLM to edit an existing file based on natural language instructions.
    """
    if not is_safe_path(filepath):
        print(f"Security Error: Attempted to read file outside of allowed directory: {filepath}")
        return False

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("GOOGLE_API_KEY not found. AI edit disabled.")
        return False

    try:
        # Load existing content
        with open(filepath, "r", encoding="utf-8") as f:
            current_content = f.read()

        llm = GoogleGenAI(model="models/gemini-2.5-flash", api_key=api_key)

        system_prompt = f"""
        You are a senior software engineer.
        Your task is to EDIT an existing file based on the user's instruction.
        Return ONLY the full new content of the file.
        Do not include markdown code blocks or explanations.

        File to edit: {filepath}
        Current content:
        ---
        {current_content}
        ---
        """

        response = llm.complete(f"{system_prompt}\n\nInstruction: {instruction}")

        new_content = response.text.strip()
        if new_content.startswith("```"):
            # Remove any markdown markers if the model included them
            lines = new_content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            new_content = "\n".join(lines).strip()

        return edit_file(filepath, new_content)

    except Exception as e:
        print(f"Error editing file with Gemini: {e}")
        return False

def scaffold_component(name, target_dir, prompt):
    """
    Uses Gemini LLM to generate a real monorepo component with multiple files.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("GOOGLE_API_KEY not found. Falling back to mock scaffolding.")
        mock_files = {
            "main.py": f"# {name} generated by Monorepo Agent (MOCK)\ndef run():\n    print('Hello from {name}')",
            "README.md": f"# {name}\n\nGenerated for: {prompt}"
        }
        return create_component_files(name, target_dir, mock_files)

    try:
        # Use gemini-2.5-flash as requested by user
        llm = GoogleGenAI(model="models/gemini-2.5-flash", api_key=api_key)

        system_prompt = """
        You are a monorepo component scaffolder.
        You MUST return ONLY a JSON object where keys are filenames and values are the file content.
        Do not include any other text, markdown blocks, or explanation.
        The component is a new service in a monorepo.
        Focus on providing a clean, working template based on the user description.
        Example format:
        {"main.py": "print('hello')", "README.md": "# My Service"}
        """

        user_prompt = f"Create a new component named '{name}' with the following description: {prompt}"

        response = llm.complete(f"{system_prompt}\n\n{user_prompt}")

        response_text = response.text.strip()

        # Robust JSON extraction for scaffolding
        # Find the first { and the last } in the text
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')

        if start_idx != -1 and end_idx != -1:
            json_block = response_text[start_idx:end_idx+1]
            files_data = json.loads(json_block)
        else:
            # Fallback if no JSON-like structure is found
            print(f"Failed to find JSON block in Gemini response: {response_text[:100]}...")
            return False
        return create_component_files(name, target_dir, files_data)

    except Exception as e:
        print(f"Error scaffolding component with Gemini: {e}")
        return False

def create_component_files(name, target_dir, files_data):
    """
    Physically creates the files on disk for a scaffolded component.
    """
    # Sanitize name and target_dir
    if ".." in name or "/" in name or "\\" in name:
        print(f"Security Error: Invalid component name: {name}")
        return False

    if not is_safe_path(target_dir):
        print(f"Security Error: Invalid target directory: {target_dir}")
        return False

    component_path = (Path(target_dir) / name).resolve()

    try:
        if component_path.exists():
            print(f"Component {name} already exists at {component_path}")
            return False

        os.makedirs(component_path, exist_ok=True)
        for filename, content in files_data.items():
            # Sanitize filename within the component
            if ".." in filename or filename.startswith("/") or filename.startswith("\\"):
                print(f"Skipping potentially malicious file: {filename}")
                continue

            file_path = component_path / filename
            # edit_file already checks is_safe_path
            edit_file(str(file_path), content)

        print(f"Scaffolded component {name} in {target_dir}")
        return True
    except Exception as e:
        print(f"Error creating files: {e}")
        return False

def ai_fix_file(filepath, command, error_message):
    """
    Uses Gemini to fix a file based on a command execution error.
    """
    if not is_safe_path(filepath):
        return False

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return False

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            current_content = f.read()

        llm = GoogleGenAI(model="models/gemini-2.5-flash", api_key=api_key)

        system_prompt = f"""
        You are a self-healing system.
        A command failed and you need to fix the file.

        File: {filepath}
        Command: {command}
        Error: {error_message}

        Current Content:
        ---
        {current_content}
        ---

        Return ONLY the full corrected content of the file.
        Do not include explanations or markdown blocks.
        """

        response = llm.complete(system_prompt)
        new_content = response.text.strip()

        # Clean markdown
        if new_content.startswith("```"):
            lines = new_content.splitlines()
            if lines[0].startswith("```"): lines = lines[1:]
            if lines and lines[-1].startswith("```"): lines = lines[:-1]
            new_content = "\n".join(lines).strip()

        return edit_file(filepath, new_content)
    except Exception as e:
        print(f"Error in AI self-healing: {e}")
        return False

def ai_generate_commit_message(diff):
    """
    Uses Gemini to generate a commit message based on the git diff.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return "chore: update code"

    try:
        llm = GoogleGenAI(model="models/gemini-2.5-flash", api_key=api_key)
        system_prompt = (
            "You are a git expert. Generate a short, descriptive commit message "
            "based on the following diff. Use conventional commits format."
        )
        response = llm.complete(f"{system_prompt}\n\nDiff:\n{diff[:2000]}")
        return response.text.strip().replace('"', '')
    except Exception:
        return "chore: update code"

def git_commit_changes():
    """
    Stages all changes, generates an AI commit message, and commits.
    """
    try:
        # Check if there are changes
        diff_res = subprocess.run(["git", "diff", "HEAD"], capture_output=True, text=True)
        if not diff_res.stdout.strip():
            # Check for staged changes
            staged_diff = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True)
            if not staged_diff.stdout.strip():
                return {"status": "no changes", "message": "No hay cambios para comitear."}

        # Stage all
        subprocess.run(["git", "add", "."], check=True)

        # Get diff for AI
        full_diff = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True).stdout

        # Generate message
        message = ai_generate_commit_message(full_diff)

        # Commit
        result = subprocess.run(["git", "commit", "-m", message], capture_output=True, text=True)
        if result.returncode == 0:
            return {"status": "success", "message": message}
        else:
            return {"status": "error", "message": result.stderr}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def self_healing_execution(command, filepath=None, max_retries=3):
    """
    Runs a command and if it fails, attempts to heal the code using AI.
    """
    retries = 0
    history = []

    while retries < max_retries:
        print(f"Executing: {command} (Attempt {retries + 1})")
        result = run_command(command)

        if result["returncode"] == 0:
            return {"status": "success", "result": result, "history": history}

        if filepath and os.path.exists(filepath):
            print(f"Command failed. Attempting AI fix for {filepath}...")
            history.append(f"Attempt {retries+1} failed: {result['stderr'][:200]}...")
            if ai_fix_file(filepath, command, result["stderr"]):
                retries += 1
            else:
                break
        else:
            return {"status": "failed", "result": result, "history": history}

    return {"status": "failed", "result": result, "history": history}

if __name__ == "__main__":
    res = run_command("ls -l")
    print(res["stdout"])
