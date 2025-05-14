import os
import threading
import time
from typing import List, Callable, Set, Dict

from ..Procedure import Procedure


class CustomFileWatcher:
    def __init__(self, original_directory,
                 procedure: Procedure, file_paths: List[str], on_file_change: Callable[[str, Procedure, str], None]):
        self.file_paths = {os.path.abspath(p) for p in file_paths}
        self.procedure = procedure
        self.on_file_change = on_file_change
        self.original_directory = original_directory
        self.file_mtimes: Dict[str, float] = {}
        self.recently_modified: Set[str] = set()
        self.should_run = True
        self.polling_thread = None

        for path in self.file_paths:
            if os.path.exists(path):
                self.file_mtimes[path] = os.path.getmtime(path)

    def start_watching(self):
        """Start the file polling thread"""
        if self.polling_thread is None:
            self.should_run = True
            self.polling_thread = threading.Thread(target=self._poll_for_changes, daemon=True)
            self.polling_thread.start()

    def stop_watching(self):
        """Stop the file polling thread"""
        self.should_run = False
        if self.polling_thread:
            self.polling_thread.join(timeout=1.0)
            self.polling_thread = None

    def _poll_for_changes(self):
        """Poll files for changes periodically"""
        while self.should_run:
            for file_path in self.file_paths:
                if os.path.exists(file_path):
                    current_mtime = os.path.getmtime(file_path)

                    # Check if file was modified (or is new)
                    if file_path not in self.file_mtimes or current_mtime > self.file_mtimes[file_path]:
                        self.file_mtimes[file_path] = current_mtime

                        # Avoid rapid duplicate notifications
                        if file_path in self.recently_modified:
                            continue

                        self.recently_modified.add(file_path)
                        threading.Timer(0.5, lambda fp=file_path: self.recently_modified.discard(fp)).start()

                        self.on_file_change(self.original_directory, self.procedure, file_path)

                else:
                    # File doesn't exist yet but is in our watch list
                    # We'll check it on next poll and detect it as new when it appears
                    pass

            time.sleep(0.5)


class FileWatcher:
    def __init__(self, original_directory, procedures: List[Procedure],
                 on_file_change: Callable[[str, Procedure, str], None]):
        self.original_directory = original_directory
        self.procedures = procedures
        self.on_file_change = on_file_change
        self.is_watching = False
        self.watched_dirs = set()
        self.watched_procedures = {}
        self.file_watchers = []

        for procedure in self.procedures:
            if procedure.on_source_change_recompile:
                file_paths = [os.path.join(procedure.build_directory, file_name)
                              for file_name in procedure.source_files]
                self.watched_procedures[procedure] = file_paths

    def start(self):
        if self.is_watching:
            return

        all_watched_files = []

        for procedure, file_paths in self.watched_procedures.items():
            watcher = CustomFileWatcher(self.original_directory, procedure, file_paths, self.on_file_change)
            self.file_watchers.append(watcher)

            for file_path in file_paths:
                abs_path = os.path.abspath(file_path)
                if not os.path.exists(abs_path):
                    print(f"Warning: File not found: {abs_path}")
                    continue

                dir_path = os.path.dirname(abs_path)
                if dir_path not in self.watched_dirs:
                    self.watched_dirs.add(dir_path)

                all_watched_files.append(abs_path)

            watcher.start_watching()

        if self.watched_dirs:
            self.is_watching = True
            print(f"Watching {len(all_watched_files)} files across {len(self.watched_procedures)} procedures:")
            for file_path in all_watched_files:
                print(f"  - {file_path}")
        else:
            print("No files to watch. No procedures with on_source_change_recompile flag were found.")

    def stop(self):
        if not self.is_watching:
            return

        for watcher in self.file_watchers:
            watcher.stop_watching()

        self.file_watchers = []
        self.is_watching = False
        print("File watching stopped")