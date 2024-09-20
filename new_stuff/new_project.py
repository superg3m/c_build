import os
import subprocess
import time
from pickle import FALSE

from typing import List, Dict
from .new_compiler import Compiler
from .new_procedure import Procedure
from .globals import FATAL_PRINT, FORMAT_PRINT, UP_LEVEL, DOWN_LEVEL, GET_LEVEL, GIT_PULL, NORMAL_PRINT
from .vc_vars import vcvars

class Project:
    def __init__(self, name: str, compiler_name: str, std_version = "c11", github_root = "https://github.com/superg3m"):
        self.name: str = name
        self.std_version: str = std_version
        self.compiler_name: str = compiler_name
        self.github_root: str = github_root
        self.internal_compiler = Compiler(self.compiler_name, self.std_version)
        self.should_debug_with_visual_studio: bool = False
        self.should_rebuild_project_dependencies: bool = os.getenv("SHOULD_REBUILD", False)
        self.dependencies: List[str] = []
        self.procedures: List[Procedure] = []
        self.executable_procedures: List[Procedure] = []
        self.is_dependency: bool = os.getenv("IS_DEPENDENCY", False)

        self.__assert_std_is_valid()

    def __check_procedure_built(self, proc):
        return os.path.exists(os.path.join(proc.build_directory, proc.output_name))

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
            if not build_directory:
                FATAL_PRINT(f"build_directory is empty on a procedure")
                exit(-5)
            os.mkdir(build_directory)

        return proc

    def build(self, build_type):
        is_debug = build_type == "debug"

        FORMAT_PRINT(f"|----------------------------------------- {self.name} -----------------------------------------|")
        UP_LEVEL()
        start_time = time.perf_counter()
        if self.compiler_name == "cl":
            vcvars()

        if len(self.dependencies) != 0 and self.dependencies[0] != "":
            FORMAT_PRINT(f"{self.name} depends on:")

        true_cached = os.getcwd()
        for dependency_string in self.dependencies:
            if not dependency_string:
                continue

            UP_LEVEL()
            if not os.path.isdir(dependency_string):
                FORMAT_PRINT(f"missing {dependency_string} cloning...")
                os.system(f"git clone {self.github_root}/{dependency_string}.git")
                cached_directory_global = os.getcwd()
                os.chdir(dependency_string)
                os.system(f"pwsh -command ./bootstrap.ps1")
                os.chdir(cached_directory_global)
            else:
                GIT_PULL(dependency_string)

            cached_current_directory_global = os.getcwd()
            os.chdir(dependency_string)
            GIT_PULL("c_build")

            os.environ['COMPILER'] = self.compiler_name
            os.environ['LEVEL'] = str(GET_LEVEL())
            os.environ['IS_DEPENDENCY'] = str(True)  # Make sure it's a string
            os.environ['SHOULD_REBUILD'] = str(self.should_rebuild_project_dependencies)
            env = os.environ.copy()
            if os.name == "nt":
                subprocess.call(
                    f"python -B -m c_build_script --build_type {build_type}",
                    shell=True,
                    env=env
                )
            else:
                subprocess.call(
                    f"python3 -B -m c_build_script --build_type {build_type}",
                    shell=True,
                    env=env
                )
            os.chdir(cached_current_directory_global)

            DOWN_LEVEL()

        os.chdir(true_cached)

        for proc in self.procedures:
            print("IS BUILT: ", self.__check_procedure_built(proc), " | IS DEP: ", self.is_dependency, " | SHOULD BUILD: ", (self.should_rebuild_project_dependencies == False))
            if self.__check_procedure_built(proc) and self.is_dependency and (self.should_rebuild_project_dependencies == False):
                NORMAL_PRINT(f"Already built procedure: {os.path.join(proc.build_directory,proc.output_name)}, skipping...")
                continue
            self.internal_compiler.compile_procedure(proc, is_debug)


        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        DOWN_LEVEL()
        FORMAT_PRINT(f"|------------------------------- Time elapsed: {elapsed_time:.2f} seconds -------------------------------|")

    def inject_as_argument(self, arg):
        self.internal_compiler.compiler_command.append(arg)

    def set_project_dependencies(self, project_dependency_strings):
        for dependency_string in project_dependency_strings:
            if not dependency_string:
                continue

            self.dependencies.append(dependency_string)

    def set_rebuild_project_dependencies(self, should_rebuild_project_dependencies):
        print("BEFORE ASSIGNMENT: ", os.getenv("SHOULD_REBUILD", "DONT HAVE IT"))
        self.should_rebuild_project_dependencies = os.getenv("SHOULD_REBUILD", should_rebuild_project_dependencies)
        print("AFTER ASSIGNMENT: ", self.should_rebuild_project_dependencies)

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