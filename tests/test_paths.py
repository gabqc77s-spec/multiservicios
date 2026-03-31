import os
from pathlib import Path
from src.agent import is_safe_path, edit_file, create_component_files

def test_path_normalization():
    print("--- Testing Path Normalization ---")

    # Test cases for mixed slashes
    paths = [
        "packages/test/main.py",
        "packages\\test\\main.py",
        "packages/test\\main.py"
    ]

    base_dir = os.getcwd()
    for p in paths:
        resolved = Path(p).resolve()
        safe = is_safe_path(p, base_dir=base_dir)
        print(f"Path: {p:30} | Resolved: {resolved.as_posix():60} | Safe: {safe}")
        assert safe == True

def test_scaffolding_paths():
    print("\n--- Testing Scaffolding Path Construction ---")

    name = "path-test-service"
    target_dir = "packages"
    files_data = {
        "main.py": "print('hello')",
        "/absolute/path/fail.py": "should be stripped",
        "subdir/config.json": "{}"
    }

    # Clean up before test
    target_path = Path(target_dir) / name
    if target_path.exists():
        import shutil
        shutil.rmtree(target_path)

    success = create_component_files(name, target_dir, files_data)
    assert success == True

    # Check for correct locations (no smashing)
    expected_main = target_path / "main.py"
    expected_config = target_path / "subdir" / "config.json"
    smashed_path = Path("packages") / (name + "main.py")

    print(f"Checking {expected_main.as_posix()} exists: {expected_main.exists()}")
    print(f"Checking {expected_config.as_posix()} exists: {expected_config.exists()}")
    print(f"Checking smashed path {smashed_path.as_posix()} DOES NOT exist: {not smashed_path.exists()}")

    assert expected_main.exists()
    assert expected_config.exists()
    assert not smashed_path.exists()

    # Verify absolute path was stripped correctly to be relative to component root
    # files_data had "/absolute/path/fail.py"
    stripped_path = target_path / "absolute/path/fail.py"
    print(f"Checking stripped absolute path {stripped_path.as_posix()} exists: {stripped_path.exists()}")
    assert stripped_path.exists()

if __name__ == "__main__":
    try:
        test_path_normalization()
        test_scaffolding_paths()
        print("\n✅ PATH TESTS PASSED")
    except AssertionError as e:
        print(f"\n❌ PATH TESTS FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        exit(1)
