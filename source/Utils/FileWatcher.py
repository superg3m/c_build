import os
import threading
from typing import List, Callable, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent

from ..Procedure import Procedure

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
                self.on_file_change(self.procedure, event.src_path)


class FileWatcher:
    def __init__(self, procedures: List[Procedure], on_file_change: Callable[[Procedure, str], None]):
        self.procedures = procedures
        self.on_file_change = on_file_change
        self.observer = None
        self.is_watching = False
        self.watched_dirs = set()
        self.watched_procedures = {}

        for procedure in self.procedures:
            print(f"WOW: what")
            if procedure.on_source_change_recompile:
                file_paths = [os.path.join(procedure.build_directory, file_name)
                              for file_name in procedure.source_files]
                self.watched_procedures[procedure] = file_paths
                print(f"WOW: {file_paths}")

    def start(self):
        if self.is_watching:
            return

        self.observer = Observer()
        all_watched_files = []

        for procedure, file_paths in self.watched_procedures.items():
            handler = FileWatcherEventHandler(procedure, file_paths, self.on_file_change)

            for file_path in file_paths:
                abs_path = os.path.abspath(file_path)
                if not os.path.exists(abs_path):
                    print(f"Warning: File not found: {abs_path}")
                    continue

                dir_path = os.path.dirname(abs_path)

                if dir_path not in self.watched_dirs:
                    self.watched_dirs.add(dir_path)
                    self.observer.schedule(handler, dir_path, recursive=False)

                all_watched_files.append(abs_path)

        if self.watched_dirs:
            self.observer.start()
            self.is_watching = True
            print(f"Watching {len(all_watched_files)} files across {len(self.watched_procedures)} procedures:")
            for file_path in all_watched_files:
                print(f"  - {file_path}")
        else:
            print("No files to watch. No procedures with on_source_change_recompile flag were found.")

    def stop(self):
        if not self.is_watching:
            return

        self.observer.stop()
        self.observer.join()
        self.is_watching = False
        print("File watching stopped")
