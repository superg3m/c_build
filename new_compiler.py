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

### USAGE CODE

funcs = print, int, float
argss = ("hello", "world"), (1, ), (1.0, )

def set_up_action_table():
    #arguments get resolved
    # functions are known as a constant

    # = [funcs, arguments]

for f, a, in zip(funcs, argss):
    f(*a)

for i in range(CompilerAction.COUNT):
    compiler_action_lookup_table[compile_type][i]




# #### While compiling do work on another dependency/procedure
# subprocess.Popen does exactly what you want.

# from subprocess import Popen
# p = Popen(['watch', 'ls']) # something long running
# # ... do other stuff while subprocess is running
# p.terminate()

# (Edit to complete the answer from comments)

# The Popen instance can do various other things like you can poll() it to see if it is still running, and you can communicate() with it to send it data on stdin, and wait for it to terminate.
