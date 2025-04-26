import os
import threading
from typing import List, Callable, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent

from source.Procedure import Procedure


class FileWatcherEventHandler(FileSystemEventHandler):
    def __init__(self, procedure: Procedure, file_paths: List[str], on_file_change: Callable[[Procedure, str], None]):
        self.file_paths = {os.path.abspath(p) for p in file_paths}
        self.procedure = procedure
        self.on_file_change = on_file_change
        self.recently_modified: Set[str] = set()
        super().__init__()

    def on_modified(self, event):
        if not event.is_directory and not isinstance(event, FileModifiedEvent):
            return

        file_path = os.path.abspath(event.src_path)
        if file_path in self.file_paths:
            if file_path in self.recently_modified:
                return

            self.recently_modified.add(file_path)
            threading.Timer(0.5, lambda: self.recently_modified.discard(file_path)).start()

            self.on_file_change(self.procedure, event.src_path)

    def on_created(self, event):
        if not event.is_directory and isinstance(event, FileCreatedEvent):
            file_path = os.path.abspath(event.src_path)
            if file_path in self.file_paths:
                self.on_file_change(file_path)


class FileWatcher:
    def __init__(self, procedure: Procedure, on_file_change: Callable[[Procedure, str], None]):
        self.procedure = procedure
        self.files_to_watch = procedure.source_files
        self.on_file_change = on_file_change
        self.observer = None
        self.is_watching = False
        self.watched_dirs = set()

    def start(self):
        if self.is_watching:
            return

        self.observer = Observer()
        handler = FileWatcherEventHandler(self.procedure, self.files_to_watch, self.on_file_change)

        for file_path in self.files_to_watch:
            if not os.path.exists(file_path):
                print(f"Warning: File not found: {file_path}")
                continue

            dir_path = os.path.dirname(os.path.abspath(file_path))

            if dir_path not in self.watched_dirs:
                self.watched_dirs.add(dir_path)
                self.observer.schedule(handler, dir_path, recursive=False)

        self.observer.start()
        self.is_watching = True

    def stop(self):
        if not self.is_watching:
            return

        self.observer.stop()
        self.observer.join()
        self.is_watching = False