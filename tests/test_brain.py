import os
import shutil
from src.brain import create_or_load_index, INDEX_DIR

def test_create_or_load_index_placeholder(tmp_path):
    # This is a bit tricky since brain uses a global INDEX_DIR
    # For testing, we can check if it creates the directory.
    if os.path.exists(INDEX_DIR):
        shutil.rmtree(INDEX_DIR)

    index = create_or_load_index(".")
    assert os.path.exists(INDEX_DIR)
    assert os.path.exists(os.path.join(INDEX_DIR, "index_status.json"))

    # Second call should "load" it
    index_2 = create_or_load_index(".")
    assert os.path.exists(INDEX_DIR)
