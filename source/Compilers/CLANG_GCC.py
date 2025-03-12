from typing import List

compiler_lookup_table: List[str] = [
    "-std=",              # STD_VERSION
    None,                 # NO_LOGO
    "-c",                 # OBJECT_FLAG
    "-o",                 # OUTPUT_FLAG
    "-D",                 # COMPILE_TIME_DEFINE_FLAG
    None,                 # MULTI_THREADING
    "-fsanitize=address", # ADDRESS_SANITIZER
    "-W",                 # WARNING_LEVEL
    "-w",                 # DISABLE_WARNINGS
    "-Wno-",              # DISABLE_SPECIFIC_WARNING
    None,                 # REPORT_FULL_PATH
    "-shared",            # DYNAMIC_LIB
    "-Werror"             # WARNINGS_AS_ERRORS
]

