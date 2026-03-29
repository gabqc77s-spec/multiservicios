import os
import shutil
from src.scanner import scan_directory

def test_scanner_edge_cases(tmp_path):
    # 1. Empty directory
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    # 2. Hidden directory (should be ignored)
    hidden_dir = tmp_path / ".hidden"
    hidden_dir.mkdir()
    (hidden_dir / "secret.txt").write_text("shhh")

    # 3. Excluded directory (should be ignored)
    node_modules = tmp_path / "node_modules"
    node_modules.mkdir()
    (node_modules / "pkg.js").write_text("console.log(1)")

    # 4. Nested structure
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    (app_dir / "main.py").write_text("print(1)")

    graph = scan_directory(str(tmp_path))

    nodes = {n["id"] for n in graph["nodes"]}

    assert "empty" in nodes
    assert "app" in nodes
    assert "app/main.py" in nodes

    assert ".hidden" not in nodes
    assert ".hidden/secret.txt" not in nodes
    assert "node_modules" not in nodes

    print("Scanner granular audit passed!")

if __name__ == "__main__":
    import pathlib
    test_scanner_edge_cases(pathlib.Path("/tmp/scanner_test"))
