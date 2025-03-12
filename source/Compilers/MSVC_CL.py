from enum import Enum
from typing import List

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

compiler_lookup_table: List[str] = [
    "/std:",              # STD_VERSION
    "/nologo",            # NO_LOGO
    "/c",                 # OBJECT_FLAG
    "/Fe:",               # OUTPUT_FLAG
    "/D",                 # COMPILE_TIME_DEFINE_FLAG
    "/MP",                # MULTI_THREADING
    "/fsanitize=address", # ADDRESS_SANITIZER
    "/W",                 # WARNING_LEVEL
    "/W0",                # DISABLE_WARNINGS
    "/wd",                # DISABLE_SPECIFIC_WARNING
    "/FC",                # REPORT_FULL_PATH
    "/LD",                # DYNAMIC_LIB
    "/WX"                 # WARNINGS_AS_ERRORS
]

class MSVC_CL_Compiler:
    def __init__(self):
        self.debug: bool = False
        self.compiler_name: str = ""
        self.programming_language: PL = PL.INVALID
        self.compiler_warning_level: str = ""
        self.compiler_disable_specific_warnings: List[str] = []
        self.compiler_treat_warnings_as_errors: bool = False
        self.compiler_disable_warnings: bool = False
        self.compiler_disable_sanitizer: bool = False