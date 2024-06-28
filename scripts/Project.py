import json
import os
import subprocess
import sys
import time

from Procedure import Procedure
from typing import List, Dict, Union

RED: str = '\033[91m'
GREEN: str = '\033[92m'
BLUE: str = '\033[94m'
CYAN: str = '\033[96m'
WHITE: str = '\033[97m'
YELLOW: str = '\033[93m'
MAGENTA: str = '\033[95m'
GREY: str = '\033[90m'
BLACK: str = '\033[90m'
DEFAULT: str = '\033[0m'

JSON_CONFIG_PATH: str = "./c_build_config.json"


def parse_json_file(file_path: str):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in '{file_path}': {e}")
        return None


def find_vs_path():
    vswhere_path = r"C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe"
    result = subprocess.run(
        [vswhere_path, "-latest", "-requires", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64", "-property",
         "installationPath"], capture_output=True, text=True)

    if result.returncode == 0:
        return result.stdout.strip()
    else:
        print("Could not find Visual Studio installation path.")
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
        print(f"{RED}Visual Studio not found.{DEFAULT}")
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
    def __init__(self, json_data: Dict[str, Union[str, bool, List[str], Dict]]) -> None:
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

        for key, value in json_data.items():
            if isinstance(value, dict):
                build_procedure: Procedure = Procedure(key, self.compiler_type, self.std_version, value)
                self.procedures.append(build_procedure)
                if self.execute_procedure_string == build_procedure.output_name:
                    self.execute_procedure = build_procedure

    def build_dependencies(self, debug):
        if len(self.project_dependency_strings) == 0 or not self.project_dependency_strings[0]:
            print(f"{CYAN}[{self.name}] depends on nothing{DEFAULT}")
            return

        print(f"{BLUE}[{self.name}] depends on: {DEFAULT}")
        for dependency_string in self.project_dependency_strings:
            print(f"{BLUE} - {dependency_string} {DEFAULT}")
            if not os.path.exists(dependency_string):
                print(f"{BLUE}missing {dependency_string} cloning...{DEFAULT}")
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
            current_dir = os.getcwd()  # Get current script's directory
            bootstrap_script = os.path.join(current_dir, 'c-build', 'bootstrap.ps1')
            build_script = os.path.join(current_dir, 'build.ps1')
            os.system(f"powershell {bootstrap_script} -compiler_type {self.compiler_type}")
            os.system(f"powershell {build_script}")
            os.chdir(cached_current_directory_global)

    def build_procedures(self, debug: bool):
        for procedure in self.procedures:
            if self.should_rebuild_project_dependencies:
                procedure.build(debug)
            else:
                procedure.build_no_check(debug)

    def build_project(self, debug):
        print(f"{GREEN}|--------------- Started Building {self.name} ---------------|{DEFAULT}")
        start_time = time.time()
        self.build_dependencies(debug)
        self.build_procedures(debug)
        end_time = time.time()
        elapsed_time = end_time - start_time

        print(f"{GREEN}|--------------- Time elapsed: {elapsed_time:.2f} seconds ---------------|{DEFAULT}")

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
