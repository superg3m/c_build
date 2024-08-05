import json
import os
import subprocess
import sys
import time

from procedure import Procedure
from typing import List, Dict, Union
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
    def __init__(self, is_dependency: bool = False):
        json_data = parse_json_file(JSON_CONFIG_PATH)
        self.is_dependency = is_dependency

        self.name: str = json_data["project_name"]
        self.compiler_type: str = json_data["compiler_type"]
        self.github_root = json_data["github_root"]

        if self.compiler_type == "cl":
            set_vs_environment()

        self.compiler = Compiler(json_data)

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
                os.system(f"git clone https://github.com/superg3m/{dependency_string}.git")

            cached_current_directory_global = os.getcwd()
            os.chdir(dependency_string)
            dependency: Project = Project()
            dependency.should_rebuild_project_dependencies = self.should_rebuild_project_dependencies
            dependency.is_dependency = True
            self.project_dependencies.append(dependency)
            os.chdir(cached_current_directory_global)

        self.procedures: List[Procedure] = []
        self.executable_name: str = json_data["execute"]
        self.executable_procedure: Union[Procedure, None] = None

        for key, value in json_data.items():
            if isinstance(value, dict):
                build_procedure: Procedure = Procedure(key, self.compiler_type, self.std_version, value)
                self.procedures.append(build_procedure)
                if self.executable_name == build_procedure.output_name:
                    self.executable_procedure = build_procedure

    def build_dependency(self, parent_name: str, dependency, debug):
        FORMAT_PRINT(f"[{self, parent_name}] depends on:")

        FORMAT_PRINT(f"- {dependency.name}")
        if not os.path.exists(dependency.name):
            FORMAT_PRINT(f"missing {dependency.name} cloning...")
            os.system(f"git clone {self.github_root}/{dependency.name}.git")
        else:
            GIT_PULL(dependency.name)

        if not os.path.exists("c-build"):
            os.system("git clone https://github.com/superg3m/c-build.git")
        else:
            GIT_PULL("c-build")

        cached_current_directory_global = os.getcwd()
        os.chdir(dependency.name)
        dependency.build_project(debug)
        os.chdir(cached_current_directory_global)

    def build_dependencies(self, parent_name, project_dependencies):
        for dependency in project_dependencies:
            self.build_dependency(parent_name, dependency)

    def build_procedures(self):
        for procedure in self.procedures:
            check = self.should_rebuild_project_dependencies and self.is_dependency
            self.compiler.build_procedure(check, procedure)

    def execute_procedure(self):
        if not self.executable_procedure:
            temp = []
            for procedure in self.procedures:
                if procedure.should_build_executable:
                    temp.append(procedure.output_name)

            FATAL_PRINT(f"Invalid executable name, expected: {temp} | got: {self.executable_name}")
            return
        if not self.executable_procedure.is_built():
            self.build_project(False)

        self.executable_procedure.execute()

    def debug_procedure(self):
        self.build_project(True)

        self.executable_procedure.debug(self.debug_with_visual_studio)

    def build_project(self, debug):
        FORMAT_PRINT(f"|--------------- Started Building {self.name} ---------------|")
        UP_LEVEL()
        start_time = time.time()
        self.compiler.debug = debug
        self.dependency_builder = debug
        self.dependency_builder.build_dependencies(self.project_dependencies)
        self.build_procedures()
        end_time = time.time()
        elapsed_time = end_time - start_time
        DOWN_LEVEL()
        FORMAT_PRINT(f"|--------------- Time elapsed: {elapsed_time:.2f} seconds ---------------|")

    def clean_dependencies(self):
        for dependency in self.project_dependencies:
            cached_path_name = os.getcwd()
            os.chdir(dependency.name)
            dependency.clean_project()
            os.chdir(cached_path_name)

    def clean_procedures(self):
        for procedure in self.procedures:
            procedure.clean()

    def clean_project(self):
        self.clean_dependencies()
        self.clean_procedures()
