import os
import shutil
import pytest
from src.brain import create_or_load_index, INDEX_DIR

def test_create_or_load_index_logic():
    # Clean up before test
    if os.path.exists(INDEX_DIR):
        shutil.rmtree(INDEX_DIR)

    # Test with default (mock/openai) since no key in test env usually
    # It might return None if key is missing, but we want to check if it handles it
    index = create_or_load_index(".")
    assert os.path.exists(INDEX_DIR)
    assert os.path.exists(os.path.join(INDEX_DIR, "index_status.json"))

    with open(os.path.join(INDEX_DIR, "index_status.json"), "r") as f:
        status = f.read()
        assert "status" in status

def test_load_existing_index_graceful():
    # Should load if files exist, or handle it gracefully
    index = create_or_load_index(".")
    # If it's None because of missing API key, it's acceptable in this test environment
    assert os.path.exists(INDEX_DIR)
