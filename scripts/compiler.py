# Configuration
    # address sanitizers
    # disable warnings
    # inject into compiler args
    # specify version of c
    # have default specification

# init compiler
    # setup compiler arguments
    # source files
    # include paths
    # additional libs
    # additional libs paths
    # compile time defines
    # invoke compiler

#compilers to support
    # gcc
    # cl
    # cc
    # clang

class Compiler:
    def __init__(self, compiler_json) -> None:
        compiler_type = compiler_json["compiler type"]
        compiler_version = compiler_json["compiler version"]
        compiler_disable_warnings = compiler_json["compiler disable warnings"]
        compile_time_defines = compiler_json["compile time defines"]

        compiler_build_in_debug = compiler_json["compiler build in debug"]
        compiler_build_static_lib = compiler_json["compiler build in debug"]
        compiler_build_dynamic_lib = compiler_json["compiler build in debug"]

        compiler_source_files = compiler_json["compiler source files"]
        compiler_include_directories = compiler_json["compiler include directories"]
        compiler_additional_lib_directories = compiler_json["compiler library directories"]
        compiler_additional_libs = compiler_json["compiler libs"]

        compiler_inject_into_args = compiler_json["compiler inject as argument"]

        compiler_arguments = ""
        # compiler type (cl, gcc, cc, clang)


