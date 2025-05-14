import os
import threading
import time
import logging
from typing import List, Callable, Set, Dict, Optional

from ..Procedure import Procedure

# I just had claude generate this to replace watch dog...
class CustomFileWatcher:
    def __init__(self, original_directory,
                 procedure: Procedure, file_paths: List[str], on_file_change: Callable[[str, Procedure, str], None]):
        self.file_paths = {os.path.abspath(p) for p in file_paths}
        self.procedure = procedure
        self.on_file_change = on_file_change
        self.original_directory = original_directory
        self.file_mtimes: Dict[str, float] = {}
        self.recently_modified: Set[str] = set()
        self.should_run = False
        self.polling_thread: Optional[threading.Thread] = None
        self.lock = threading.RLock()

        for path in self.file_paths:
            try:
                if os.path.exists(path):
                    self.file_mtimes[path] = os.path.getmtime(path)
            except Exception as e:
                logging.warning(f"Failed to get mtime for {path}: {e}")

    def start_watching(self):
        """Start the file polling thread"""
        with self.lock:
            if self.polling_thread is not None and self.polling_thread.is_alive():
                return

            self.should_run = True
            self.polling_thread = threading.Thread(target=self._poll_for_changes, daemon=True)
            self.polling_thread.start()

    def stop_watching(self):
        """Stop the file polling thread"""
        with self.lock:
            self.should_run = False

        if self.polling_thread:
            try:
                if self.polling_thread.is_alive():
                    self.polling_thread.join(timeout=1.0)
            except Exception as e:
                logging.warning(f"Error while stopping thread: {e}")
            finally:
                self.polling_thread = None

    def _poll_for_changes(self):
        """Poll files for changes periodically"""
        while self.should_run:
            try:
                self._check_files_for_changes()
                time.sleep(0.5)
            except Exception as e:
                logging.error(f"Error in file polling: {e}")
                # Add a small delay to avoid CPU spinning on persistent errors
                time.sleep(0.1)

    def _check_files_for_changes(self):
        """Check all watched files for changes"""
        for file_path in self.file_paths:
            try:
                if not os.path.exists(file_path):
                    # File doesn't exist yet but is in our watch list
                    # We'll check it on next poll and detect it as new when it appears
                    continue

                current_mtime = os.path.getmtime(file_path)

                with self.lock:
                    is_new = file_path not in self.file_mtimes
                    is_modified = not is_new and current_mtime > self.file_mtimes[file_path]

                    if is_new or is_modified:
                        self.file_mtimes[file_path] = current_mtime
                        if file_path in self.recently_modified:
                            continue

                        self.recently_modified.add(file_path)
                        self._schedule_clear_modified_flag(file_path)


                if is_new or is_modified:
                    self.on_file_change(self.original_directory, self.procedure, file_path)

            except FileNotFoundError:
                pass
            except Exception as e:
                logging.warning(f"Error checking file {file_path}: {e}")

    def _schedule_clear_modified_flag(self, file_path: str):
        """Schedule removal of a file from recently_modified set safely"""

        def clear_flag():
            try:
                with self.lock:
                    self.recently_modified.discard(file_path)
            except Exception as e:
                logging.warning(f"Error clearing modified flag: {e}")

        timer = threading.Timer(0.5, clear_flag)
        timer.daemon = True
        timer.start()


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
        self.lock = threading.RLock()

        self._setup_watched_procedures()

    def _setup_watched_procedures(self):
        """Initialize the watched procedures dict"""
        for procedure in self.procedures:
            if procedure.on_source_change_recompile:
                file_paths = [os.path.join(procedure.build_directory, file_name)
                              for file_name in procedure.source_files]
                self.watched_procedures[procedure] = file_paths

    def start(self):
        with self.lock:
            if self.is_watching:
                return

            all_watched_files = []
            self.file_watchers = []

            for procedure, file_paths in self.watched_procedures.items():
                try:
                    watcher = CustomFileWatcher(self.original_directory, procedure, file_paths, self.on_file_change)
                    self.file_watchers.append(watcher)

                    for file_path in file_paths:
                        abs_path = os.path.abspath(file_path)
                        if not os.path.exists(abs_path):
                            logging.warning(f"Warning: File not found: {abs_path}")
                            continue

                        dir_path = os.path.dirname(abs_path)
                        if dir_path not in self.watched_dirs:
                            self.watched_dirs.add(dir_path)

                        all_watched_files.append(abs_path)

                    watcher.start_watching()
                except Exception as e:
                    logging.error(f"Error setting up watcher for {procedure}: {e}")

            if self.watched_dirs:
                self.is_watching = True
                print(f"Watching {len(all_watched_files)} files across {len(self.watched_procedures)} procedures:")
                for file_path in all_watched_files:
                    print(f"  - {file_path}")
            else:
                print("No files to watch. No procedures with on_source_change_recompile flag were found.")

    def stop(self):
        with self.lock:
            if not self.is_watching:
                return

            for watcher in self.file_watchers:
                try:
                    watcher.stop_watching()
                except Exception as e:
                    logging.error(f"Error stopping watcher: {e}")

            self.file_watchers = []
            self.is_watching = False
            print("File watching stopped")