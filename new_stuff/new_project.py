import os
import subprocess
import time
from typing import List, Dict
from new_compiler import Compiler
from new_procedure import Procedure
from globals import FATAL_PRINT, FORMAT_PRINT, UP_LEVEL, DOWN_LEVEL

class Project:
    def __init__(self, name: str, compiler_name: str, std_version = "c11", github_root = "https://github.com/superg3m"):
        self.name: str = name
        self.std_version: str = std_version

        self.compiler_name: str = compiler_name
        self.github_root: str = github_root
        FORMAT_PRINT(f"|----------------------------------------- Start -----------------------------------------|")
        UP_LEVEL()
        self.start_time = time.perf_counter()
        self.internal_compiler: Compiler = Compiler(compiler_name, std_version)
        self.should_debug_with_visual_studio = False
        self.should_rebuild_project_dependencies = False
        self.dependencies: List[Project] = []
        self.procedures: List[Procedure] = []
        self.executable_procedures: List[Procedure] = []

        self.__assert_std_is_valid()


    def __assert_std_is_valid(self):
        acceptable_versions: Dict[int, List[str]] = {
            0: ["c11", "c17", "clatest"],  # CL
            1: ["c89", "c90", "c99", "c11", "c17", "c18", "c23"],  # GCC_CC_CLANG
        }

        ret = self.std_version in acceptable_versions[self.internal_compiler.type.value]

        if not ret:
            FORMAT_PRINT(f"Std version: {self.std_version} not supported, choose one of these {acceptable_versions[self.internal_compiler.type.value]}")

    def set_executables_to_run(self, executable_names):
        executable_map = {}
        for proc in self.procedures:
            if proc:
                executable_map[proc.output_name] = proc

        for i in range(len(executable_names)):
            if executable_names[i] in executable_map.keys():
                self.executable_procedures.append(executable_map[executable_names[i]])
            else:
                FATAL_PRINT(f"Invalid executable name(s), expected: {executable_map.keys()} | got: {executable_names}")
                exit(-15)

    def add_procedure(self, build_directory):
        proc = Procedure(build_directory)
        self.procedures.append(proc)

        if not os.path.exists(build_directory):
            FATAL_PRINT(f"Can't find path at {build_directory}")
            exit(-15)

        return proc

    def build(self):
        for proc in self.procedures:
            self.internal_compiler.compile_procedure(proc)

        end_time = time.perf_counter()
        elapsed_time = end_time - self.start_time
        DOWN_LEVEL()
        FORMAT_PRINT(f"|------------------------------- Time elapsed: {elapsed_time:.2f} seconds -------------------------------|")

    def inject_as_argument(self, arg):
        self.internal_compiler.compiler_command.append(arg)

    def set_project_dependencies(self, project_dependency_strings):
        for dependency_string in project_dependency_strings:
            if not dependency_string:
                continue

            UP_LEVEL()

            if not os.path.isdir(dependency_string):
                FORMAT_PRINT(f"missing {dependency_string} cloning...")
                os.system(f"git clone {self.github_root}/{dependency_string}.git")

            cached_current_directory_global = os.getcwd()
            os.chdir(dependency_string)
            subprocess.call(f"c_build.py {self.compiler_name}", shell=True)
            os.chdir(cached_current_directory_global)

            DOWN_LEVEL()

    def set_rebuild_project_dependencies(self, should_rebuild_project_dependencies):
        self.should_rebuild_project_dependencies = should_rebuild_project_dependencies

    def set_debug_with_visual_studio(self, should_debug_with_visual_studio):
        self.should_debug_with_visual_studio = should_debug_with_visual_studio

    def set_compiler_warning_level(self, warning_level_string):
        self.internal_compiler.set_warning_level(warning_level_string)

    def disable_specific_warnings(self, specific_warnings):
        self.internal_compiler.disable_specific_warnings(specific_warnings)

    def set_compile_time_defines(self, compile_time_defines: List[str]):
        self.internal_compiler.set_compile_time_defines(compile_time_defines)

    def set_treat_warnings_as_errors(self, is_error):
        self.internal_compiler.set_treat_warnings_as_errors(is_error)