import os
import subprocess
import sys
from typing import List, Dict, Union

RED: str = '\033[91m'
GREEN: str = '\033[92m'
BLUE: str = '\033[94m'
CYAN: str = '\033[96m'
WHITE: str = '\033[97m'
YELLOW: str = '\033[93m'
MAGENTA: str = '\033[95m'
GREY: str = '\033[90m'
BLACK: str = '\033[90m'
DEFAULT: str = '\033[0m'


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
        self.source_paths: str = json_data["source_paths"]
        self.additional_libs: List[str] = json_data["additional_libs"]

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
                lib_command.append(lib)

        cached_current_directory = os.curdir
        error_occurred = False
        try:
            subprocess.run(lib_command, capture_output=True, text=True, check=True)
        except FileNotFoundError:
            print(f"{RED}lib command not found{DEFAULT}")
            error_occurred = True
        except subprocess.CalledProcessError as e:
            print(f"{RED}======= Error: static lib creation failed with return code {e.returncode} ======={DEFAULT}")
            if e.stdout:
                error_lines = e.stdout.splitlines()
                for line in error_lines:
                    if line.strip() and not line.endswith(".c"):
                        print(f"{RED}Compilation error | {line.strip()}{DEFAULT}")

            print(f"{MAGENTA}Lib Command: {e.args[1]}{DEFAULT}")
            print(f"{RED}=========================================================================={DEFAULT}")
            error_occurred = True
        finally:
            os.chdir(cached_current_directory)
            if error_occurred:
                sys.exit(-1)

    def build_no_check(self, debug: bool) -> None:
        compiler_index: int = self.get_compiler_index()

        no_logo: List[Union[str, None]] = ["/nologo", None, None]
        standard_flag: List[str] = ["/std:", "-std=", "-std="]
        object_flag: List[str] = ["/c", "-c", "-c"]
        output_flag: List[str] = ["/Fe", "-o", "-o"]
        compile_time_define_flag: List[str] = ["/D", "-D", "-D"]

        compiler_command: List[str] = [self.compiler_type, self.source_paths]

        if no_logo[compiler_index]:
            compiler_command.append(no_logo[compiler_index])

        if self.std_is_valid():
            compiler_command.append(f"{standard_flag[compiler_index]}{self.std_version}")
        else:
            print(MAGENTA + f"Std version: {self.std_version} not supported, falling back on default" + DEFAULT)

        for define in self.compile_time_defines:
            compiler_command.append(f"{compile_time_define_flag[compiler_index]}{define}")

        if self.should_build_static_lib:
            compiler_command.append(object_flag[compiler_index])
        else:
            if self.should_build_dynamic_lib:
                compiler_command.append("/LD")

            compiler_command.append(f"{output_flag[compiler_index]}{self.output_name}")
            compiler_command.extend(self.additional_libs)

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

        # Check if the directory exists, and if not, create it
        if not os.path.exists(self.build_directory):
            os.makedirs(self.build_directory)
            print(BLUE + f"Directory {self.build_directory} created." + DEFAULT)

        cached_current_directory = os.getcwd()
        error_occurred = False
        try:
            os.chdir(self.build_directory)
            result = subprocess.run(compiler_command, capture_output=True, text=True, check=True)

            if self.should_build_static_lib:
                self.build_static_lib()

            print(f"{GREEN}Compilation of {self.output_name} successful{DEFAULT}")
        except FileNotFoundError:
            print(f"{RED}{self.compiler_type} compiler not found{DEFAULT}")
            error_occurred = True
        except subprocess.CalledProcessError as e:
            print(f"{RED}=========== Error: Compilation failed with return code {e.returncode} ==========={DEFAULT}")
            if e.stdout:
                error_lines = e.stdout.splitlines()
                for line in error_lines:
                    if line.strip() and not line.endswith(".c"):
                        print(f"{RED}Compilation error | {line.strip()}{DEFAULT}")

            print(f"{MAGENTA}Compiler Command: {e.args[1]}{DEFAULT}")
            print(f"{RED}=========================================================================={DEFAULT}")
            error_occurred = True
        finally:
            os.chdir(cached_current_directory)
            if error_occurred:
                sys.exit(-1)

    def build(self, debug: bool) -> None:
        if self.is_built():
            print(CYAN + f"Already built procedure: {self.output_name}, skipping..." + DEFAULT)
            return

        self.build_no_check(debug)

    def __str__(self):
        output = f"{CYAN}================================================\n"
        output += f"{GREEN}directory: {self.build_directory}\n"
        output += f"compiler: {self.compiler_type}\n"
        output += f"should_build_executable: {self.should_build_executable}\n"
        output += f"should_build_static_lib: {self.should_build_static_lib}\n"
        output += f"should_build_dynamic_lib: {self.should_build_dynamic_lib}\n"
        output += f"output_name: {self.output_name}\n"
        output += f"compile_time_defines: {self.compile_time_defines}\n"
        output += f"include_paths: {self.include_paths}\n"
        output += f"source_paths: {self.source_paths}\n"
        output += f"additional_libs: {self.additional_libs}{DEFAULT}\n"
        output += f"{CYAN}================================================{DEFAULT}\n"
        return output
