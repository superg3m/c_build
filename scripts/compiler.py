# Configuration
# address sanitizers
# disable warnings
# inject into compiler args
# specify version of c
# have default specification
import os
from typing import List


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

# build with multi-threading!!!
# build with multi-threading!!!
# build with multi-threading!!!
# build with multi-threading!!!
# build with multi-threading!!!
# build with multi-threading!!!
# build with multi-threading!!!
# build with multi-threading!!!
# build with multi-threading!!!
# build with multi-threading!!!
# build with multi-threading!!!
# build with multi-threading!!! /MP /WX


class Compiler:
    def __init__(self, compiler_json, debug) -> None:
        # global
        self.compiler_type: str = compiler_json["compiler_type"]
        self.std_version: str = compiler_json["std_version"]
        self.compiler_disable_warnings: List[str] = compiler_json["compiler_disable_warnings"]
        self.additional_libs: List[str] = compiler_json["additional_libs"]
        self.compiler_warning_level: str = compiler_json["compiler_warning_level"]
        self.compiler_treat_warnings_as_errors: bool = compiler_json["compiler_treat_warnings_as_errors"]
        self.compiler_inject_into_args = compiler_json["compiler inject as argument"]
        self.compiler_debug: bool = debug

        # procedure specific
        self.output_name: str = ""
        self.compile_time_defines: List[str] = []
        self.should_build_executable: bool = False
        self.should_build_static_lib: bool = False
        self.should_build_dynamic_lib: bool = False
        self.source_files: List[str] = []
        self.include_paths: List[str] = []
        self.additional_libs: List[str] = []
        self.inject_into_args: List[str] = []

        self.compiler_arguments = ""

        # compiler type (cl, gcc, cc, clang)

    def setup_procedure(self, build_directory: str, procedure_json):
        self.output_name = procedure_json["output_name"]
        self.compile_time_defines = procedure_json["compile_time_defines"]

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

        self.source_files = procedure_json["source_files"]
        self.include_paths = procedure_json["include_paths"]
        self.additional_libs = procedure_json["additional_libs"]

    def get_compiler_index(self) -> int:
        compiler_index: int = -1
        if self.compiler_type == "cl":
            compiler_index = 0
        elif self.compiler_type == "gcc":
            compiler_index = 1
        elif self.compiler_type == "cc":
            compiler_index = 2
        elif self.compiler_type == "clang":
            compiler_index = 3
        return compiler_index

    def std_is_valid(self) -> bool:
        compiler_index: int = self.get_compiler_index()

        cl_lookup_table: List[str] = ["c11", "c17", "clatest"]
        gcc_lookup_table: List[str] = ["c89", "c90", "c99", "c11", "c17", "c18", "c23"]
        cc_lookup_table: List[str] = ["c89", "c90", "c99", "c11", "c17", "c18", "c23"]
        clang_lookup_table: List[str] = ["c89", "c90", "c99", "c11", "c17", "c18", "c23"]
        compiler_lookup_table: List[List[str]] = [
            cl_lookup_table,
            gcc_lookup_table,
            cc_lookup_table,
            clang_lookup_table
        ]

        if self.std_version in compiler_lookup_table[compiler_index]:
            return True
        else:
            return False
