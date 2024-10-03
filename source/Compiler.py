import os
import subprocess
from enum import Enum
from typing import List, Dict

from .Utilities import FORMAT_PRINT, NORMAL_PRINT, build_static_lib, FATAL_PRINT

class CompilerType(Enum):
    INVALID = -1
    CL = 0
    GCC_CC_CLANG = 1


class CompilerAction(Enum):
    NO_ACTION = -1
    STD_VERSION = 0
    NO_LOGO = 1
    OBJECTS_ONLY = 2
    OUTPUT = 3
    COMPILE_TIME_DEFINES = 4
    MULTI_THREADING = 5
    ADDRESS_SANITIZER = 6
    WARNING_LEVEL = 7
    DISABLE_WARNINGS = 8
    DISABLE_SPECIFIC_WARNING = 9
    REPORT_FULL_PATH = 10
    DYNAMIC_LIB = 11
    WARNINGS_AS_ERRORS = 12


compiler_lookup_table: List[List[str]] = [
    [ # Compiler CL
        "/std:",  # STD_VERSION
        "/nologo",  # NO_LOGO
        "/c",  # OBJECT_FLAG
        "/Fe:",  # OUTPUT_FLAG
        "/D",  # COMPILE_TIME_DEFINE_FLAG
        "/MP",  # MULTI_THREADING
        "/fsanitize=address",  # ADDRESS_SANITIZER
        "/W",   # WARNING_LEVEL
        "/W0",  # DISABLE_WARNINGS
        "/wd",  # DISABLE_SPECIFIC_WARNING
        "/FC",   # REPORT_FULL_PATH
        "/LD",    # DYNAMIC_LIB
        "/WX"    # WARNINGS_AS_ERRORS
    ],

    [ # Compiler GCC_CC_CLANG
        "-std=",  # STD_VERSION
        None,  # NO_LOGO
        "-c",  # OBJECT_FLAG
        "-o",  # OUTPUT_FLAG
        "-D",  # COMPILE_TIME_DEFINE_FLAG
        None,  # MULTI_THREADING
        "-fsanitize=address",  # ADDRESS_SANITIZER
        "-W",  # WARNING_LEVEL
        "-w",  # DISABLE_WARNINGS
        "-Wno-",  # DISABLE_SPECIFIC_WARNING
        None,      # REPORT_FULL_PATH
        "-shared", # DYNAMIC_LIB
        "-Werror"  # WARNINGS_AS_ERRORS
    ],
]

class Compiler:
    def __init__(self):
        self.debug: bool = False
        self.compiler_name: str = ""
        self.compiler_std_version: str  = "c11"
        self.compiler_type: CompilerType = CompilerType.INVALID
        self.compiler_warning_level: str = ""
        self.compiler_disable_specific_warnings: List[str] = []
        self.compiler_treat_warnings_as_errors: bool = False

    def set_config(self, is_debug, config):
        self.debug = is_debug
        self.compiler_name = config["compiler_name"]
        self.compiler_std_version = config["compiler_std_version"]
        self.compiler_type: CompilerType = self.choose_compiler_type()
        self.compiler_warning_level = config["compiler_warning_level"]
        self.compiler_disable_specific_warnings = config["compiler_disable_specific_warnings"]
        self.compiler_treat_warnings_as_errors = config["compiler_treat_warnings_as_errors"]

    def std_is_valid(self) -> bool:
        acceptable_versions: Dict[int, List[str]] = {
            0: ["c11", "c17", "clatest"],  # CL
            1: ["c89", "c90", "c99", "c11", "c17", "c18", "c23"],  # GCC_CC_CLANG
        }

        return self.compiler_std_version in acceptable_versions[self.compiler_type.value]

    def IS_MSVC(self):
        return self.compiler_type == CompilerType.CL

    def choose_compiler_type(self):
        temp = CompilerType.INVALID
        if self.compiler_name == "cl":
            temp = CompilerType.CL
        elif self.compiler_name in ["gcc", "cc", "clang"]:
            temp = CompilerType.GCC_CC_CLANG
        return temp

    def get_compiler_lookup(self, action: CompilerAction) -> str:
        return compiler_lookup_table[self.compiler_type.value][action.value]

    def compile_procedure(self, procedure_config):
        build_directory = procedure_config["build_directory"]
        output_name = procedure_config["output_name"]
        source_files = procedure_config["source_files"]
        additional_libs = procedure_config["additional_libs"]
        compile_time_defines = procedure_config["compile_time_defines"]
        include_paths = procedure_config["include_paths"]

        should_build_executable = False
        should_build_static_lib = False
        should_build_dynamic_lib = False

        extension: str = os.path.splitext(output_name)[-1].lower()
        if extension == ".exe":
            should_build_executable = True
        elif extension in [".lib", ".a"]:
            should_build_static_lib = True
        elif extension in [".so", ".o", ".dylib"]:
            should_build_dynamic_lib = True
        else:
            should_build_executable = True  # For Linux

        compiler_command: List[str] = [self.compiler_type]
        compiler_command.extend([source for source in source_files if source])

        # Add no logo flag
        no_logo_flag = self.get_compiler_lookup(CompilerAction.NO_LOGO)
        if no_logo_flag:
            compiler_command.append(no_logo_flag)

        # Add std version flag
        std_version_flags = self.get_compiler_lookup(CompilerAction.STD_VERSION)
        if self.std_is_valid():
            compiler_command.append(f"{std_version_flags}{self.compiler_std_version}")
        else:
            FORMAT_PRINT(f"Std version: {self.compiler_std_version} not supported, falling back on default")
            compiler_command.append(f"{std_version_flags}c11")

        report_full_path_flag = self.get_compiler_lookup(CompilerAction.REPORT_FULL_PATH)
        if report_full_path_flag:
            compiler_command.append(report_full_path_flag)

        # Add compile time defines
        compile_time_define_flag = self.get_compiler_lookup(CompilerAction.COMPILE_TIME_DEFINES)
        compiler_command.extend([f"{compile_time_define_flag}{define}" for define in compile_time_defines if define])

        # Add object flag
        if should_build_static_lib:
            object_flag = self.get_compiler_lookup(CompilerAction.OBJECTS_ONLY)
            compiler_command.append(object_flag)
        else:
            if should_build_dynamic_lib:
                dynamic_lib_flag = self.get_compiler_lookup(CompilerAction.DYNAMIC_LIB)
                compiler_command.append(dynamic_lib_flag)

            # Add output flag
            output_flag = self.get_compiler_lookup(CompilerAction.OUTPUT)
            compiler_command.append(output_flag)
            compiler_command.append(output_name)

        # Add multi-threading flag
        multi_threading_flag = self.get_compiler_lookup(CompilerAction.MULTI_THREADING)
        if multi_threading_flag:
            compiler_command.append(multi_threading_flag)

        # Add warning level flag
        if self.compiler_warning_level:
            warning_level_flag = self.get_compiler_lookup(CompilerAction.WARNING_LEVEL)
            compiler_command.append(f"{warning_level_flag}{self.compiler_warning_level}")

        # Add disable warnings flag
        if self.compiler_disable_specific_warnings:
            disable_warnings_flag = self.get_compiler_lookup(CompilerAction.DISABLE_WARNINGS)
            compiler_command.append(disable_warnings_flag)

        # Add disable specific warning flag
        disable_specific_warning_flag = self.get_compiler_lookup(CompilerAction.DISABLE_SPECIFIC_WARNING)
        compiler_command.extend(
            [
             f"{disable_specific_warning_flag}{warning}"
             for warning in self.compiler_disable_specific_warnings
             if warning
            ]
        )

        # Add warnings as errors flag
        if self.compiler_treat_warnings_as_errors:
            warning_as_errors_flag = self.get_compiler_lookup(CompilerAction.WARNINGS_AS_ERRORS)
            compiler_command.append(warning_as_errors_flag)

        # Add optimization flag
        if self.debug:
            # Add address sanitizer flag
            if os.name != 'nt':
                address_sanitizer_flag = self.get_compiler_lookup(CompilerAction.ADDRESS_SANITIZER)
                compiler_command.append(address_sanitizer_flag)

            if self.IS_MSVC():
                compiler_command.append("/Od")
                compiler_command.append("/Zi")
            else:
                compiler_command.append("-g")
        else:
            if self.IS_MSVC():
                compiler_command.append("/O2")
            else:
                compiler_command.append("-O2")

        # Add include paths
        for include_path in include_paths:
            if include_path:
                if self.IS_MSVC():
                    compiler_command.append(f"/I{include_path}")
                else:
                    compiler_command.append(f"-I{include_path}")

        if not should_build_static_lib:
            if len(additional_libs) > 0 and additional_libs[0] and self.IS_MSVC():
                compiler_command.append("/link")
            compiler_command.extend([lib for lib in additional_libs if lib])

        cached_current_directory = os.getcwd()
        return_code = 0

        try:
            if not os.path.exists(build_directory):
                os.mkdir(build_directory)
            os.chdir(build_directory)
            FORMAT_PRINT(compiler_command)
            result = subprocess.run(compiler_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            for line in result.stdout.splitlines():
                NORMAL_PRINT(line.strip())

            for line in result.stderr.splitlines():
                NORMAL_PRINT(line.strip())

            FORMAT_PRINT(f"{compiler_command}")

            return_code = result.returncode
            if should_build_static_lib:
                build_static_lib(self.compiler_type, output_name, additional_libs)

            if return_code:
                FATAL_PRINT("FAILED TO COMPILE!")
                exit(-1)
            else:
                FORMAT_PRINT(f"Compilation of {output_name} successful")

        finally:
            os.chdir(cached_current_directory)