import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--build_type', default="debug", type=str, required=False, help='build_type -> { debug, release }')
parser.add_argument('--is_dependency', default="false", type=str, required=False, help='is_dependency -> { true, false }')
parser.add_argument('--execution_type', default="BUILD", type=str, required=False, help='Build type -> { BUILD, RUN, CLEAN, DEBUG }')
parser.add_argument('--compiler_name', default="INVALID_COMPILER", type=str, required=False, help='Compiler Name -> { cl, gcc, cc, clang }')