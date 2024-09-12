import json
import os
import subprocess
import sys
import time
from typing import List, Dict, Union

from procedure import Procedure
from globals import FATAL_PRINT, JSON_CONFIG_PATH, FORMAT_PRINT, UP_LEVEL, DOWN_LEVEL, GIT_PULL, set_vs_environment
from compiler import Compiler


def parse_json_file(file_path: str):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        FATAL_PRINT(f"File '{file_path}' not found.")
        return None
    except json.JSONDecodeError as e:
        FATAL_PRINT(f"Error decoding JSON in '{file_path}': {e}")
        return None


class Project:
    def __init__(self, is_dependency: bool = False, compiler_type: str = None):
        json_data = parse_json_file(JSON_CONFIG_PATH)
        self.is_dependency = is_dependency

        self.name: str = json_data["project_name"]
        if compiler_type:
            self.compiler_type = compiler_type
        else:
            self.compiler_type: str = json_data["compiler_type"]

        if self.compiler_type == "cl" and os.name == "nt":
            set_vs_environment()

        self.github_root = json_data["github_root"]

        self.compiler = Compiler(json_data, self.compiler_type)

        self.std_version: str = json_data["std_version"]
        self.debug_with_visual_studio: bool = json_data["debug_with_visual_studio"]
        self.should_rebuild_project_dependencies: bool = json_data["should_rebuild_project_dependencies"]
        self.project_dependency_strings: List[str] = json_data["project_dependencies"]
        self.project_dependencies: List[Project] = []

        for dependency_string in self.project_dependency_strings:
            if not dependency_string:
                continue

            if not os.path.isdir(dependency_string):
                FORMAT_PRINT(f"missing {dependency_string} cloning...")
                os.system(f"git clone {self.github_root}/{dependency_string}.git")

            cached_current_directory_global = os.getcwd()
            os.chdir(dependency_string)
            dependency: Project = Project(True, self.compiler_type)
            dependency.should_rebuild_project_dependencies = self.should_rebuild_project_dependencies
            self.project_dependencies.append(dependency)
            os.chdir(cached_current_directory_global)

        self.procedures: List[Procedure] = []
        self.executable_names: str = json_data["execute"]
        self.executable_procedures: List[Union[Procedure, None]] = []

        valid_names = []
        for key, value in json_data.items():
            if isinstance(value, dict):
                key = key.replace("$compiler_type", self.compiler_type)
                build_procedure = Procedure(key, self.compiler_type, self.std_version, value)
                self.procedures.append(build_procedure)
                if build_procedure.should_build_executable:
                    valid_names.append(build_procedure.output_name)

        for exe_name in self.executable_names:
            if not exe_name:
                return
            if exe_name in valid_names:
                for proc in self.procedures:
                    if proc.output_name == exe_name :
                        self.executable_procedures.append(proc)
            else:
                FATAL_PRINT(f"Invalid executable name(s), expected: {valid_names} | got: {self.executable_names}")
                sys.exit(-1)

    def build_dependency(self, dependency):
        FORMAT_PRINT(f"[{self.name}] depends on:")
        FORMAT_PRINT(f"- {dependency.name}")

        if not os.path.exists(dependency.name):
            FORMAT_PRINT(f"missing {dependency.name} cloning...")
            os.system(f"git clone {self.github_root}/{dependency.name}.git")
        else:
            GIT_PULL(dependency.name)

        if not os.path.exists("c_build"):
            os.system("git clone https://github.com/superg3m/c_build.git")
        else:
            GIT_PULL("c_build")

        cached_current_directory_global = os.getcwd()
        os.chdir(dependency.name)
        dependency.build_project(self.compiler.debug)
        os.chdir(cached_current_directory_global)

    def build_dependencies(self, project_dependencies):
        for dependency in project_dependencies:
            self.build_dependency(dependency)

    def build_procedures(self):
        for procedure in self.procedures:
            check = not self.should_rebuild_project_dependencies and self.is_dependency
            self.compiler.build_procedure(check, procedure)

    def execute_procedures(self):
        for exe_proc in self.executable_procedures:
            if not exe_proc.is_built():
                self.build_project(False)

            exe_proc.execute()

    def debug_procedure(self):
        self.build_project(True)
        self.executable_procedures[0].debug(self.debug_with_visual_studio)

    def build_project(self, debug):
        FORMAT_PRINT(f"|--------------- Started Building {self.name} ---------------|")
        UP_LEVEL()
        start_time = time.perf_counter()
        self.compiler.debug = debug
        self.build_dependencies(self.project_dependencies)
        self.build_procedures()
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        DOWN_LEVEL()
        FORMAT_PRINT(f"|--------------- Time elapsed: {elapsed_time:.2f} seconds ---------------|")

    def clean_dependencies(self):
        for dependency in self.project_dependencies:
            cached_path_name = os.getcwd()
            if not os.path.exists(dependency.name):
                continue
                
            os.chdir(dependency.name)
            dependency.clean_project()
            os.chdir(cached_path_name)

    def clean_procedures(self):
        for procedure in self.procedures:
            procedure.clean()

    def clean_project(self):
        self.clean_dependencies()
        self.clean_procedures()
