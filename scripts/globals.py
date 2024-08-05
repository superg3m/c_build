import os
import platform
import shutil
import subprocess
import sys
from typing import List

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
FATAL = "\033[41m"

JSON_CONFIG_PATH: str = "../c_build_config.json"

level = 0
indent_spaces = " " * (level * 4)


def UP_LEVEL():
    global level, indent_spaces
    level += 1
    indent_spaces = " " * (level * 4)


def DOWN_LEVEL():
    global level, indent_spaces
    level -= 1
    indent_spaces = " " * (level * 4)


def FORMAT_PRINT(msg):
    global indent_spaces
    color_lookup = [GREEN, BLUE, YELLOW, MAGENTA, CYAN, RED]
    color = color_lookup[level % len(color_lookup)]
    if msg:
        print(f"{color}{indent_spaces}{msg}{DEFAULT}")


def NORMAL_PRINT(msg):
    global indent_spaces
    if msg:
        print(f"{indent_spaces}{msg}")


def FATAL_PRINT(msg):
    global indent_spaces
    if msg:
        print(f"{FATAL}{indent_spaces}{msg}{DEFAULT}")


def GIT_PULL(path: str):
    current_directory = os.getcwd()
    os.chdir(path)
    os.system("git fetch origin -q")
    os.system("git reset --hard origin/main -q")
    os.system("git pull -q")
    os.chdir(current_directory)


def IS_WINDOWS_PROCESS_RUNNING(process_name):
    programs = str(subprocess.check_output('tasklist'))
    if process_name in programs:
        return True
    else:
        return False


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

def build_static_lib(output_name, additional_libs):
    lib_command: List[str] = []

    if platform.system() == "Windows":
        lib_command = [
            "lib",
            "/NOLOGO",
            f"/OUT:{output_name}",
            "./*.obj"
        ]
    else:
        lib_command = [
            "ar",
            "rcs",
            output_name,
            "./*.o"
        ]

    if additional_libs:
        for lib in additional_libs:
            if lib:
                lib_command.append(lib)

    error_occurred = False
    try:
        # Check if the lib/ar command exists
        if shutil.which(lib_command[0]) is None:
            raise FileNotFoundError(f"{lib_command[0]} command not found")

        result = subprocess.run(lib_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for line_2 in result.stdout.splitlines():
            NORMAL_PRINT(line_2.strip())

        for line_2 in result.stderr.splitlines():
            NORMAL_PRINT(line_2.strip())
    except FileNotFoundError:
        FATAL_PRINT(f"{lib_command[0]} command not found")
        error_occurred = True
    except subprocess.CalledProcessError as e:
        FORMAT_PRINT(f"======= Error: static lib failed with return code {e.returncode} =======")
        if e.stdout:
            error_lines = e.stdout.splitlines()
            for line_2 in error_lines:
                if line_2.strip() and not line_2.endswith(".c"):
                    FATAL_PRINT(f"Compilation error | {line_2.strip()}")

        NORMAL_PRINT(f"Lib Command: {e.cmd}")
        FORMAT_PRINT(f"==========================================================================")
        error_occurred = True
    finally:
        if error_occurred:
            sys.exit(-1)
