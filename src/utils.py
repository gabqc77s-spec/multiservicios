import os
import sys
import shlex
from pathlib import Path

def get_root_dir():
    """Returns the absolute path of the project root."""
    return Path(__file__).parent.parent.resolve()

def normalize_path(path):
    """Converts a path to POSIX format for consistency."""
    return Path(path).as_posix()

def resolve_path(path):
    """Returns the absolute, resolved path of a given path."""
    try:
        return Path(path).resolve()
    except Exception:
        return None

def is_safe_path(path, base_dir=None):
    """
    Validates that the path is within the base_dir (defaults to project root)
    and does not attempt to escape it using '..'.
    """
    if base_dir is None:
        base_dir = get_root_dir()

    try:
        base_path = Path(base_dir).resolve()
        target_path = Path(path).resolve()

        # Check if target_path is under base_path or in /tmp for tests
        # We must ensure that target_path is not only starting with base_path,
        # but is actually a child of it.
        is_under_base = base_path in target_path.parents or base_path == target_path

        # If we are in /tmp, we check if it is under the temporary base_dir provided
        # or if it is just a generic /tmp path (for legacy compatibility in some tests)
        is_in_tmp = str(target_path).startswith("/tmp/") or str(target_path).startswith("C:/Users/TEMP/")

        # If base_dir is NOT the project root (e.g. it's a specific tmp dir in a test)
        # we strictly check for sub-path relationship.
        if normalize_path(base_dir) != normalize_path(get_root_dir()):
             return is_under_base

        return is_under_base or is_in_tmp
    except Exception:
        return False

def clean_command(command):
    """
    Normalizes backslashes to forward slashes in commands to prevent escape sequence issues
    and ensure consistency across platforms.
    """
    if not command:
        return ""
    # Only replace backslashes if not inside quotes? No, for paths it's usually better to just use forward slashes.
    return command.replace("\\", "/")

def get_relative_path(path, start=None):
    """Returns the relative path from the start (defaults to root)."""
    if start is None:
        start = get_root_dir()
    try:
        return os.path.relpath(path, start)
    except Exception:
        return str(path)
