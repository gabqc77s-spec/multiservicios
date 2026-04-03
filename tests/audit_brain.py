import os
import shutil
import json
from src.brain import create_or_load_index, configure_gemini

def test_brain_persistence(tmp_path):
    os.environ["GOOGLE_API_KEY"] = "mock_key"
    # Change to tmp_path to isolate .brain
    os.chdir(tmp_path)

    # SimpleDirectoryReader needs at least one file or it might raise/fail
    with open("initial.py", "w") as f:
        f.write("# initial file")

    # 1. Test index creation
    index = create_or_load_index()
    assert os.path.exists(".brain")
    # Persistence might take a second if async, but here it's sync
    # Verify index_status.json at least
    assert os.path.exists(".brain/index_status.json")

    # 2. Test force_refresh
    # Add a new file
    with open("new_file.py", "w") as f:
        f.write("def hello(): print('world')")

    index2 = create_or_load_index(force_refresh=True)
    with open(".brain/index_status.json", "r") as f:
        status = json.load(f)
        assert status["status"] == "indexed"

    print("Brain granular audit passed!")

if __name__ == "__main__":
    import pathlib
    test_brain_persistence(pathlib.Path("/tmp/brain_test"))
