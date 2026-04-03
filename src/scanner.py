import os
import json
from pathlib import Path
try:
    from .utils import normalize_path, resolve_path, get_relative_path
except ImportError:
    from utils import normalize_path, resolve_path, get_relative_path

def scan_directory(root_path="."):
    """
    Scans the directory and maps the file system architecture.
    Identifies relevant files like .env, venv, node_modules (to exclude from deep scan but mark existence).
    """
    graph = {
        "nodes": [],
        "edges": []
    }

    exclude_dirs = {".git", "node_modules", "venv", ".brain", "__pycache__", ".pytest_cache", ".vscode", "dist", "build"}

    root = Path(root_path).resolve()

    for current_path, dirs, files in os.walk(root):
        # Filter directories to avoid scanning excluded ones deeply
        # Also ignore hidden folders starting with a dot
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith(".")]

        rel_current = get_relative_path(current_path, root)
        if rel_current == ".":
            rel_current = "root"

        graph["nodes"].append({
            "id": rel_current,
            "type": "directory",
            "path": normalize_path(current_path)
        })

        for file in files:
            file_path = Path(current_path) / file
            rel_file = get_relative_path(file_path, root)

            graph["nodes"].append({
                "id": rel_file,
                "type": "file",
                "path": normalize_path(file_path),
                "extension": file_path.suffix
            })

            graph["edges"].append({
                "from": rel_current,
                "to": rel_file,
                "type": "contains"
            })

        # Add edges for directories (parent -> child)
        if rel_current != "root":
            parent_dir = get_relative_path(os.path.dirname(current_path), root)
            if parent_dir == ".":
                parent_dir = "root"
            graph["edges"].append({
                "from": parent_dir,
                "to": rel_current,
                "type": "contains"
            })

    return graph

def save_graph(graph, output_file="graph.json"):
    with open(output_file, "w") as f:
        json.dump(graph, f, indent=4)
    print(f"Graph saved to {output_file}")

if __name__ == "__main__":
    project_graph = scan_directory()
    save_graph(project_graph)
