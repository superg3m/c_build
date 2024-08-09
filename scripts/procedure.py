import glob
import os
import subprocess
import sys
from typing import List, Dict, Union
from globals import FORMAT_PRINT, FATAL_PRINT, MAGENTA, NORMAL_PRINT, IS_WINDOWS_PROCESS_RUNNING


class Procedure:
    def __init__(self, build_directory: str, compiler_type: str, std_version: str, json_data) -> None:
        self.build_directory: str = build_directory
        self.compiler_type: str = compiler_type
        self.std_version: str = std_version
        self.output_name: str = json_data["output_name"]

        self.should_build_executable: bool = False
        self.should_build_static_lib: bool = False
        self.should_build_dynamic_lib: bool = False

        extension: str = os.path.splitext(self.output_name)[-1].lower()

        if extension == ".exe":
            self.should_build_executable = True
        elif extension in [".lib", ".a"]:
            self.should_build_static_lib = True
        elif extension in [".so", ".o", ".dylib"]:
            self.should_build_dynamic_lib = True
        else:
            self.should_build_executable = True  # For Linux

        self.compile_time_defines: List[str] = json_data["compile_time_defines"]

        self.validate_list_of_strings(json_data, "source_files")
        self.validate_list_of_strings(json_data, "additional_libs")
        self.validate_list_of_strings(json_data, "include_paths")

        self.source_files: List[str] = json_data["source_files"]
        self.resolve_source_file_glob()  # for ./*.c
        self.additional_libs: List[str] = json_data["additional_libs"]
        self.include_paths: List[str] = json_data["include_paths"]

        self.replace_compiler_type()

    def replace_compiler_type(self):
        # Replace in string attributes
        for attr, value in self.__dict__.items():
            if isinstance(value, str):
                placeholder = "$compiler_type"
                if placeholder in value:
                    self.__dict__[attr] = value.replace(placeholder, self.compiler_type)

            # Replace in list of strings attributes
            elif isinstance(value, list) and all(isinstance(val, str) for val in value):
                placeholder = "$compiler_type"
                self.__dict__[attr] = [
                    val.replace(placeholder, self.compiler_type) for val in value
                ]

    def resolve_source_file_glob(self):
        resolved_files = []
        for pattern in self.source_files:
            if '*' in pattern:
                directory = os.path.dirname(pattern)
                base_name = os.path.basename(pattern)

                current_directory = os.getcwd()

                try:
                    os.chdir(directory)
                    resolved_files.extend(f"{directory}/{glob.glob(base_name)}")
                finally:
                    os.chdir(current_directory)
            else:
                resolved_files.append(pattern)

        self.source_files = resolved_files

    def validate_list_of_strings(self, data, key):
        if not isinstance(data.get(key), list) or not all(isinstance(item, str) for item in data[key]):
            FATAL_PRINT(f"{key.upper()} TYPE: {type(data.get(key))}")
            FATAL_PRINT(
                f"{self.build_directory}/{self.output_name} | {key.upper()} MUST BE AN ARRAY OF STRINGS")
            sys.exit(-1)

    def is_built(self) -> bool:
        output_path: str = os.path.join(self.build_directory, self.output_name)
        return os.path.exists(output_path)

    def build(self, check_is_built, compiler):
        compiler.build_procedure(check_is_built, self)

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

    def execute(self) -> None:
        error_occurred = False
        cached_current_directory = os.getcwd()
        try:
            resolved_exe = self.output_name
            if os.name != 'nt':  # Not Windows
                resolved_exe = f"./{self.output_name}"

            os.chdir(self.build_directory)
            os.system(resolved_exe)
        except FileNotFoundError:
            FATAL_PRINT(f"executable not found")
            error_occurred = True
        finally:
            os.chdir(cached_current_directory)
            if error_occurred:
                sys.exit(-1)

    def debug(self, is_debugging_with_visual_studio: bool):
        debugger = ["raddbg", "devenv"]
        debug_command = [debugger[is_debugging_with_visual_studio], self.output_name]
        error_occurred = False
        cached_current_directory = os.getcwd()

        try:
            os.chdir(self.build_directory)
            debugger_name = debugger[is_debugging_with_visual_studio]

            # Check if the debugger process is already running
            debugger_running = IS_WINDOWS_PROCESS_RUNNING(debugger_name)
            if debugger_running:
                NORMAL_PRINT(f"Debugger already running attaching to process...")
            else:
                process = subprocess.Popen(debug_command)
                NORMAL_PRINT(f"Started new debugger with command: {debug_command}")

        except FileNotFoundError:
            FATAL_PRINT(f"Executable not found")
            error_occurred = True
        finally:
            os.chdir(cached_current_directory)
            if error_occurred:
                sys.exit(-1)
