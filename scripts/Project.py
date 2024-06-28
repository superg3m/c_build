import json
import os
import subprocess
import sys
import time

from Procedure import Procedure
from typing import List, Dict, Union
from globals import GREEN, RED, MAGENTA, DEFAULT, CYAN, BLUE, JSON_CONFIG_PATH, FORMAT_PRINT, UP_LEVEL, DOWN_LEVEL

def parse_json_file(file_path: str):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        FORMAT_PRINT(f"File '{file_path}' not found.", RED)
        return None
    except json.JSONDecodeError as e:
        FORMAT_PRINT(f"Error decoding JSON in '{file_path}': {e}", RED)
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
        FORMAT_PRINT(f"{RED}Visual Studio not found.{DEFAULT}", RED)
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
    def __init__(self) -> None:
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

        self.procedures: List[Procedure] = []

        self.execute_procedure_string: str = json_data["execute"]
        self.execute_procedure: Union[Procedure, None] = None
        self.depth = 0

        for key, value in json_data.items():
            if isinstance(value, dict):
                build_procedure: Procedure = Procedure(key, self.compiler_type, self.std_version, value)
                self.procedures.append(build_procedure)
                if self.execute_procedure_string == build_procedure.output_name:
                    self.execute_procedure = build_procedure

    def build_dependencies(self, debug):
        if len(self.project_dependency_strings) == 0 or not self.project_dependency_strings[0]:
            FORMAT_PRINT(f"[{self.name}] depends on nothing", CYAN)
            return

        FORMAT_PRINT(f"{BLUE}[{self.name}] depends on: {DEFAULT}", BLUE)
        for dependency_string in self.project_dependency_strings:
            FORMAT_PRINT(f"- {dependency_string}", BLUE)
            if not os.path.exists(dependency_string):
                FORMAT_PRINT(f"missing {dependency_string} cloning...", BLUE)
                os.system(f"git clone https://github.com/superg3m/{dependency_string}.git")
            else:
                cached_current_directory_local = os.getcwd()
                os.chdir(dependency_string)
                os.system("git fetch origin -q")
                os.system("git reset --hard origin/main -q")
                os.system("git pull -q")
                os.chdir(cached_current_directory_local)

            if not os.path.exists("c-build"):
                os.system("git clone https://github.com/superg3m/c-build.git")
            else:
                cached_current_directory_local = os.getcwd()
                os.chdir(dependency_string)
                os.system("git fetch origin -q")
                os.system("git reset --hard origin/main -q")
                os.system("git pull -q")
                os.chdir(cached_current_directory_local)

            cached_current_directory_global = os.getcwd()
            os.chdir(dependency_string)
            dependency: Project = Project()
            dependency.should_rebuild_project_dependencies = self.should_rebuild_project_dependencies
            dependency.depth = self.depth + 4
            dependency.build_project(debug)
            os.chdir(cached_current_directory_global)

    def build_procedures(self, debug: bool):
        for procedure in self.procedures:
            if self.should_rebuild_project_dependencies:
                procedure.build_no_check(debug)
            else:
                procedure.build(debug)

    def build_project(self, debug):
        indent = " " * self.depth  # Indentation based on depth parameter
        FORMAT_PRINT(f"|--------------- Started Building {self.name} ---------------|", GREEN)
        UP_LEVEL()
        start_time = time.time()
        FORMAT_PRINT(f"|--------------- Building Dependencies ---------------|", MAGENTA)
        self.build_dependencies(debug)
        FORMAT_PRINT(f"|-----------------------------------------------------|", MAGENTA)

        FORMAT_PRINT(f"|--------------- Building Procedures ---------------|", MAGENTA)
        self.build_procedures(debug)
        FORMAT_PRINT(f"|-----------------------------------------------------|", MAGENTA)

        end_time = time.time()
        elapsed_time = end_time - start_time
        DOWN_LEVEL()
        FORMAT_PRINT(f"|--------------- Time elapsed: {elapsed_time:.2f} seconds ---------------|", GREEN)

    def __str__(self):
        output = f"{CYAN}================== name: {self.name} ==================\n"
        output += f"{GREEN}name: {self.name}\n"
        output += f"compiler: {self.compiler_type}\n"
        output += f"debug_with_visual_studio: {self.debug_with_visual_studio}\n"
        output += f"should_rebuild_project_dependencies: {self.should_rebuild_project_dependencies}\n"
        output += f"project_dependencies: {self.project_dependencies}\n"
        output += f"std_version: {self.std_version}\n"
        output += f"{CYAN}================================================{DEFAULT}\n"
        return output
