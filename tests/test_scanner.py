import os
import json
from src.scanner import scan_directory, save_graph

def test_scan_directory():
    graph = scan_directory(".")
    assert "nodes" in graph
    assert "edges" in graph
    # Check if root is present
    node_ids = [node["id"] for node in graph["nodes"]]
    assert "root" in node_ids

def test_save_graph(tmp_path):
    graph = {"nodes": [], "edges": []}
    file = tmp_path / "test_graph.json"
    save_graph(graph, str(file))
    assert os.path.exists(file)
    with open(file, "r") as f:
        data = json.load(f)
    assert data == graph
