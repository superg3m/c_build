import os
from pydoc import resolve
from typing import List
from xml.etree.ElementInclude import include


class Procedure:
    def __init__(self, build_directory: str):
        self.build_directory: str = build_directory
        self.output_name: str = ""

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

        self.source_files: List[str] = []
        self.include_paths: List[str] = []
        self.additional_libs: List[str] = []
        self.compile_time_defines: List[str] = []

    def __resolve_source_glob(self, maybe_source_glob, is_recursive) -> List[str]:
        resolved_files = []
        for pattern in maybe_source_glob:
            if '*.c' in pattern:
                directory = os.path.dirname(pattern)
                for file in os.listdir():
                    if file.endswith('.c'):
                        resolved_files.append(f"{directory}/{file}")
            elif '.c' in maybe_source_glob:
                resolved_files.append(pattern)

        return resolved_files

    def set_output_name(self, output_name):
        self.output_name = output_name

    def set_source_files(self, source_files):
        for source_glob in source_files:
            self.source_files += self.__resolve_source_glob(source_glob, False)

        # print(self.source_files)

    def set_include_paths(self, include_paths):
        self.include_paths = include_paths

    def set_additional_libs(self, additional_libs):
       self.additional_libs = additional_libs

    def set_compile_time_defines(self, compile_time_defines):
        self.compile_time_defines = compile_time_defines