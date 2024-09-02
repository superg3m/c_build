import os
import subprocess
from builtins import function
from enum import Enum
from typing import List, Union, Dict

from procedure import Procedure
from globals import FORMAT_PRINT, set_vs_environment, NORMAL_PRINT, FATAL_PRINT, build_static_lib


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
    COUNT = 11


compiler_lookup_table: List[List[str]] = [
    # Compiler CL
    [
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
        "/FC"   # REPORT_FULL_PATH
    ],
    # Compiler GCC_CC_CLANG
    [
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
        None      # REPORT_FULL_PATH
    ],
]

compiler_action_lookup_table: List[List[function]] = [
    # Compiler CL
    [
        check_version_and_add()# STD_VERSION
        # NO_LOGO
        # OBJECT_FLAG
        # OUTPUT_FLAG
        # COMPILE_TIME_DEFINE_FLAG
        # MULTI_THREADING
        # ADDRESS_SANITIZER
        # WARNING_LEVEL
        # DISABLE_WARNINGS
        # DISABLE_SPECIFIC_WARNIN       # REPORT_FULL_PATH
    ],
    # Compiler GCC_CC_CLANG
    [
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
        None      # REPORT_FULL_PATH
    ],
]

def setup_action_table(procedure: Procedure):
    action_table = []

    # Actions need to be ordered by action order in the enum

    # Output Action
    action_table.append((perform_output_action, (procedure.output_name,)))

    # Compiler Version Action
    action_table.append((perform_std_version_action, (procedure.std_version,)))

    # Disable Warnings Action
    if procedure.compiler_disable_warnings:
        action_table.append((perform_disable_warnings_action, ()))

    # Warning Level Action
    action_table.append((perform_warning_level_action, (procedure.compiler_warning_level,)))

    # Treat Warnings as Errors Action
    if procedure.compiler_treat_warnings_as_errors:
        action_table.append((perform_treat_warnings_as_errors_action, ()))

    # Disable Specific Warnings Action
    if procedure.compiler_disable_specific_warnings:
        for warning in procedure.compiler_disable_specific_warnings:
            action_table.append((perform_disable_specific_warning_action, (warning,)))

    # Compile Time Defines Action
    for define in procedure.compile_time_defines:
        action_table.append((perform_compile_time_define_action, (define,)))

    # Include Paths Action
    for include_path in procedure.include_paths:
        action_table.append((perform_include_paths_action, (include_path,)))

    # Source Files Action
    for source_file in procedure.source_files:
        action_table.append((perform_source_files_action, (source_file,)))

    # Additional Libraries Action
    for additional_lib in procedure.additional_libs:
        action_table.append((perform_additional_libs_action, (additional_lib,)))

    # Return the populated action table
    return action_table
