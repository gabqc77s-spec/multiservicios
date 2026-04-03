import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
try:
    from .utils import normalize_path
except ImportError:
    from utils import normalize_path

class ProjectChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
        self.last_triggered = 0

    def on_modified(self, event):
        if event.is_directory:
            return

        # Avoid duplicate triggers within a short window (debounce)
        now = time.time()
        if now - self.last_triggered < 5:
            return

        # Filter for relevant files
        filename = event.src_path
        if any(filename.endswith(ext) for ext in [".py", ".md", ".json", ".txt"]):
            if ".brain" not in filename and "__pycache__" not in filename:
                print(f"File modified: {filename}. Triggering RAG refresh.")
                self.callback()
                self.last_triggered = now

def start_watcher(root_dir, refresh_callback):
    """
    Starts a background thread to watch for file changes and refresh RAG.
    """
    event_handler = ProjectChangeHandler(refresh_callback)
    observer = Observer()
    observer.schedule(event_handler, root_dir, recursive=True)
    observer.start()
    return observer
