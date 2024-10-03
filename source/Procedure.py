import os
import subprocess
from typing import Dict

from .Utilities import IS_WINDOWS, FATAL_PRINT, FORMAT_PRINT, IS_WINDOWS_PROCESS_RUNNING, NORMAL_PRINT


class Procedure:
    def __init__(self, MANAGER_COMPILER, procedure_config: Dict):
        self.MANAGER_COMPILER = MANAGER_COMPILER
        self.build_directory = procedure_config["build_directory"]
        self.output_name = procedure_config["output_name"]
        self.source_files = procedure_config["source_files"]
        self.additional_libs = procedure_config["additional_libs"]
        self.compile_time_defines = procedure_config["compile_time_defines"]
        self.include_paths = procedure_config["include_paths"]

    def compile(self):
        self.MANAGER_COMPILER.compile_procedure(self)

    def clean(self):
        current_dir = os.getcwd()
        current_dir = current_dir.replace("\\", "/")

        current_dir = current_dir + self.build_directory.replace("./", "/")
        if not os.path.exists(self.build_directory):
            return
        FORMAT_PRINT(f"Cleaning: {current_dir}")
        for filename in os.listdir(self.build_directory):
            file_path = os.path.join(self.build_directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    if file_path.endswith(".c") or file_path.endswith(".cpp") or file_path.endswith(".sln"):
                        continue

                    os.unlink(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))


    def debug(self, debug_with_visual_studio):
        debugger = ["raddbg", "devenv"]
        debug_command = [debugger[debug_with_visual_studio], self.output_name]
        cached_current_directory = os.getcwd()
        try:
            os.chdir(self.build_directory)
            debugger_name = debugger[debug_with_visual_studio]

            # Check if the debugger process is already running
            debugger_running = IS_WINDOWS_PROCESS_RUNNING(debugger_name)
            if debugger_running:
                NORMAL_PRINT(f"Debugger already running attaching to process...")
            else:
                process = subprocess.Popen(debug_command)
                NORMAL_PRINT(f"Started new debugger with command: {debug_command}")

        except FileNotFoundError:
            FATAL_PRINT(f"Executable not found")
            exit(-1)
        finally:
            os.chdir(cached_current_directory)

    def run(self):
        cached_current_directory = os.getcwd()
        try:
            os.chdir(self.build_directory)
            executable_path = f"./{self.output_name}" if not IS_WINDOWS() else f".\\{self.output_name}"
            subprocess.run([executable_path])
        except FileNotFoundError:
            FATAL_PRINT(f"Executable '{self.output_name}' not found in directory '{self.build_directory}'")
            exit(-1)
        except Exception as e:
            FATAL_PRINT(f"Error running executable '{self.output_name}': {e}")
            exit(-1)
        finally:
            os.chdir(cached_current_directory)