import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--build_type', default="INVALID_BUILD_TYPE", type=str, required=False, help='build_type -> { debug, release }')
parser.add_argument('--is_dependency', default="false", type=str, required=False, help='is_dependency -> { true, false }')
parser.add_argument('--always_pull', default="true", type=str, required=False, help='is_dependency -> { true, false }')
parser.add_argument('--execution_type', default="BUILD", type=str, required=False, help='Build type -> { BUILD, RUN, CLEAN, DEBUG }')
parser.add_argument('--compiler_name', default="INVALID_COMPILER", type=str, required=False, help='Compiler Name -> { cl, gcc, cc, clang }')

def C_BUILD_BUILD_TYPE() -> str:
    return parser.parse_args().build_type

def C_BUILD_EXECUTION_TYPE() -> str:
    return parser.parse_args().execution_type

def C_BUILD_COMPILER_NAME() -> str:
    return parser.parse_args().compiler_name

def C_BUILD_IS_DEPENDENCY() -> bool:
    return parser.parse_args().is_dependency == "true"

def C_BUILD_ALWAYS_PULL() -> bool:
    return parser.parse_args().always_pull == "true"