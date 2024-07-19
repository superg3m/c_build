import json
import os
import subprocess
import sys
import time

from Procedure import Procedure
from typing import List, Dict, Union
from globals import FATAL_PRINT, JSON_CONFIG_PATH, FORMAT_PRINT, UP_LEVEL, DOWN_LEVEL, GIT_PULL


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


def find_vs_path():
    vswhere_path = r"C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe"
    result = subprocess.run(
        [vswhere_path, "-latest", "-requires", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64", "-property",
         "installationPath"], capture_output=True, text=True)

    if result.returncode == 0:
        return result.stdout.strip()
    else:
        FORMAT_PRINT("Could not find Visual Studio installation path.")
        return None


def is_cl_in_path():
    for path in os.environ.get("PATH", "").split(os.pathsep):
        if os.path.isfile(os.path.join(path, "cl.exe")) and os.path.isfile(os.path.join(path, "lib.exe")):
            return True
    return False


def set_vs_environment():
    if is_cl_in_path():
        return

    vs_path = find_vs_path()
    if not vs_path:
        FATAL_PRINT(f"Visual Studio not found.")
        return

    vcvarsall_path = os.path.join(vs_path, "VC", "Auxiliary", "Build", "vcvarsall.bat")
    temp_batch_file = "temp_env.bat"
    env_output_file = "env.txt"

    # Create a temporary batch file to capture environment variables
    with open(temp_batch_file, "w") as f:
        f.write(f"@echo off\n")
        f.write(f"call \"{vcvarsall_path}\" x64 > nul\n")  # Redirecting output to nul (null device)
        f.write(f"set > \"{env_output_file}\"\n")

    # Run the temporary batch file
    subprocess.run(temp_batch_file, shell=True)

    # Read the environment variables from the output file
    with open(env_output_file) as f:
        lines = f.readlines()

    # Set the environment variables in the current process
    for line in lines:
        if "=" in line:
            name, value = line.strip().split("=", 1)
            os.environ[name] = value

    # Clean up temporary files
    os.remove(temp_batch_file)
    os.remove(env_output_file)


class Project:
    def __init__(self):
        json_data = parse_json_file(JSON_CONFIG_PATH)
        self.name: str = json_data["project_name"]
        self.compiler_type: str = json_data["compiler_type"]
        if self.compiler_type == "cl":
            set_vs_environment()

        self.std_version: str = json_data["std_version"]
        self.debug_with_visual_studio: bool = json_data["debug_with_visual_studio"]
        self.should_rebuild_project_dependencies: bool = json_data["should_rebuild_project_dependencies"]
        self.project_dependency_strings: List[str] = json_data["project_dependencies"]
        self.project_dependencies: List[Project] = []

        FATAL_PRINT(self.project_dependency_strings)
        for dependency_string in self.project_dependency_strings:
            if not dependency_string:
                continue

            if not os.path.isdir(dependency_string):
                FORMAT_PRINT(f"missing {dependency_string} cloning...")
                os.system(f"git clone https://github.com/superg3m/{dependency_string}.git")
                continue

            cached_current_directory_global = os.getcwd()
            os.chdir(dependency_string)
            dependency: Project = Project()
            dependency.should_rebuild_project_dependencies = self.should_rebuild_project_dependencies
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

    def build_dependencies(self, debug):
        if len(self.project_dependency_strings) == 0 or not self.project_dependency_strings[0]:
            FORMAT_PRINT(f"[{self.name}] depends on nothing")
            return

        FORMAT_PRINT(f"[{self.name}] depends on:")
        FATAL_PRINT(f"LENGTH: {len(self.project_dependencies)}")
        for dependency in self.project_dependencies:
            FORMAT_PRINT(f"- {dependency.name}")
            if not os.path.exists(dependency.name):
                FORMAT_PRINT(f"missing {dependency.name} cloning...")
                os.system(f"git clone https://github.com/superg3m/{dependency.name}.git")
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

    def build_procedures(self, debug: bool):
        for procedure in self.procedures:
            if self.should_rebuild_project_dependencies:
                procedure.build_no_check(debug)
            else:
                procedure.build(debug)

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
        self.build_dependencies(debug)
        self.build_procedures(debug)
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
