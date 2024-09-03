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

    def __resolve_source_glob(self, maybe_source_glob: str, is_recursive: bool) -> List[str]:
        resolved_files = []

        if '*.c' in maybe_source_glob:
            # Determine the directory from maybe_source_glob
            source_dir = os.path.dirname(maybe_source_glob) or "."
            current_directory = os.getcwd()

            try:
                # Change to the build directory first
                os.chdir(self.build_directory)
                os.chdir(source_dir)

                if is_recursive:
                    for root, _, files in os.walk(os.getcwd()):
                        for file in files:
                            if file.endswith('.c'):
                                relative_path = source_dir + "/" + os.path.relpath(os.path.join(root, file)).replace("\\", "/")
                                resolved_files.append(relative_path)
                else:
                    # Non-recursive: list files in the specified directory
                    for file in os.listdir(os.getcwd()):
                        if file.endswith('.c'):
                            relative_path = os.path.relpath(os.path.join(source_dir, file)).replace("\\", "/")
                            resolved_files.append(relative_path)
            finally:
                # Change back to the original directory
                os.chdir(current_directory)

        elif '.c' in maybe_source_glob:
            resolved_files.append(maybe_source_glob)

        return resolved_files

    def set_output_name(self, output_name):
        self.output_name = output_name

    def set_source_files(self, source_files, recursive_search = False):
        for source_glob in source_files:
            self.source_files += self.__resolve_source_glob(source_glob, recursive_search)

        print(self.source_files)

    def set_include_paths(self, include_paths):
        self.include_paths = include_paths

    def set_additional_libs(self, additional_libs):
       self.additional_libs = additional_libs

    def set_compile_time_defines(self, compile_time_defines):
        self.compile_time_defines = compile_time_defines