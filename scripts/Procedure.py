import os
import subprocess
import sys
from typing import List, Dict, Union
from globals import FORMAT_PRINT, FATAL_PRINT, MAGENTA, NORMAL_PRINT

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
        self.include_paths: List[str] = json_data["include_paths"]

        self.validate_list_of_strings(json_data, "source_paths")
        self.validate_list_of_strings(json_data, "additional_libs")

        self.source_paths: List[str] = json_data["source_paths"]
        self.additional_libs: List[str] = json_data["additional_libs"]

    def validate_list_of_strings(self, data, key):
        if not isinstance(data.get(key), list) or not all(isinstance(item, str) for item in data[key]):
            FATAL_PRINT(f"{key.upper()} TYPE: {type(data.get(key))}")
            FATAL_PRINT(
                f"{self.build_directory}/{self.output_name} | {key.upper()} MUST BE AN ARRAY OF STRINGS")
            sys.exit(-1)


    def is_built(self) -> bool:
        output_path: str = os.path.join(self.build_directory, self.output_name)
        return os.path.exists(output_path)

    def get_compiler_index(self) -> int:
        compiler_index: int = -1
        if self.compiler_type == "cl":
            compiler_index = 0
        elif self.compiler_type == "gcc":
            compiler_index = 1
        elif self.compiler_type == "clang":
            compiler_index = 2
        return compiler_index

    def std_is_valid(self) -> bool:
        compiler_index: int = self.get_compiler_index()

        cl_lookup_table: List[str] = ["c11", "c17", "clatest"]
        gcc_lookup_table: List[str] = ["c89", "c90", "c99", "c11", "c17", "c18", "c23"]
        clang_lookup_table: List[str] = ["c89", "c90", "c99", "c11", "c17", "c18", "c23"]
        compiler_lookup_table: List[List[str]] = [cl_lookup_table, gcc_lookup_table, clang_lookup_table]

        if self.std_version in compiler_lookup_table[compiler_index]:
            return True
        else:
            return False

    def build_static_lib(self):
        lib_command: List[str] = [
            "lib",
            "/NOLOGO",
            f"/OUT:{self.output_name}",
            "./*.obj"
        ]

        if self.additional_libs:
            for lib in self.additional_libs:
                if lib:
                    lib_command.append(lib)

        error_occurred = False
        try:
            os.system(" ".join(lib_command))
        except FileNotFoundError:
            FATAL_PRINT(f"lib command not found")
            error_occurred = True
        except subprocess.CalledProcessError as e:
            FORMAT_PRINT(f"======= Error: static lib failed with return code {e.returncode} =======")
            if e.stdout:
                error_lines = e.stdout.splitlines()
                for line in error_lines:
                    if line.strip() and not line.endswith(".c"):
                        FATAL_PRINT(f"Compilation error | {line.strip()}")

            NORMAL_PRINT(f"Lib Command: {e.cmd}")
            FORMAT_PRINT(f"==========================================================================")
            error_occurred = True
        finally:
            if error_occurred:
                sys.exit(-1)

    def build_no_check(self, debug: bool) -> None:
        compiler_index: int = self.get_compiler_index()

        no_logo: List[Union[str, None]] = ["/nologo", None, None]
        standard_flag: List[str] = ["/std:", "-std=", "-std="]
        object_flag: List[str] = ["/c", "-c", "-c"]
        output_flag: List[str] = ["/Fe:", "-o", "-o"]
        compile_time_define_flag: List[str] = ["/D", "-D", "-D"]

        compiler_command: List[str] = [self.compiler_type]

        for source in self.source_paths:
            if source:
                compiler_command.append(source)

        if no_logo[compiler_index]:
            compiler_command.append(no_logo[compiler_index])

        if self.std_is_valid():
            compiler_command.append(f"{standard_flag[compiler_index]}{self.std_version}")
        else:
            FORMAT_PRINT(f"Std version: {self.std_version} not supported, falling back on default")

        for define in self.compile_time_defines:
            compiler_command.append(f"{compile_time_define_flag[compiler_index]}{define}")

        if self.should_build_static_lib:
            compiler_command.append(object_flag[compiler_index])
        else:
            if self.should_build_dynamic_lib:
                compiler_command.append("/LD")

            compiler_command.append(f"{output_flag[compiler_index]}")
            compiler_command.append(f"{self.output_name}")

            if self.additional_libs:
                for lib in self.additional_libs:
                    if lib:
                        compiler_command.append(lib)

        if debug:
            if self.compiler_type == "cl":
                compiler_command.append("/Od")
                compiler_command.append("/Zi")
            else:
                compiler_command.append("-g")
        else:
            if self.compiler_type == "cl":
                compiler_command.append("/O2")
            else:
                compiler_command.append("-O2")

        if not os.path.exists(self.build_directory):
            os.makedirs(self.build_directory)

        cached_current_directory = os.getcwd()
        error_occurred = False
        try:
            os.chdir(self.build_directory)
            result = subprocess.run(compiler_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(result.returncode, result.stdout, result.stderr)
            # os.system(" ".join(compiler_command))

            if self.should_build_static_lib:
                self.build_static_lib()

            FORMAT_PRINT(f"Compilation of {self.output_name} successful")
        except FileNotFoundError:
            FATAL_PRINT(f"{self.compiler_type} compiler not found")
            error_occurred = True
        except subprocess.CalledProcessError as e:
            FORMAT_PRINT(f"=========== Error: Compilation failed with return code {e.returncode} ===========")
            if e.stdout:
                error_lines = e.stdout.splitlines()
                for line in error_lines:
                    if line.strip() and not line.endswith(".c"):
                        FATAL_PRINT(f"Compilation error | {line.strip()}")

            NORMAL_PRINT(f"Compiler Command: {e.cmd}")
            FORMAT_PRINT(f"==========================================================================")
            error_occurred = True
        finally:
            os.chdir(cached_current_directory)
            if error_occurred:
                sys.exit(-1)

    def build(self, debug: bool) -> None:
        if self.is_built():
            NORMAL_PRINT(f"Already built procedure: {self.output_name}, skipping...")
            return

        self.build_no_check(debug)

    def execute(self) -> None:
        error_occurred = False
        cached_current_directory = os.getcwd()
        try:
            os.chdir(self.build_directory)
            os.system(self.output_name)
        except FileNotFoundError:
            FATAL_PRINT(f"executable not found")
            error_occurred = True
        finally:
            os.chdir(cached_current_directory)
            if error_occurred:
                sys.exit(-1)

    def debug(self):
        return "ffsdf"
