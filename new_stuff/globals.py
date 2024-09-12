import glob
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

JSON_CONFIG_PATH: str = "./c_build_config.json"

level: int = 0
indent_spaces: str = " " * (level * 4)

def SET_LEVEL(value: int):
    global level, indent_spaces
    level = value
    indent_spaces = " " * (level * 4)

def GET_LEVEL():
    global level
    return level

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

def build_static_lib(compiler_name, output_name, additional_libs):
    lib_command: List[str] = []

    o_files = glob.glob('*.o')
    obj_files = glob.glob('*.obj')

    object_files = o_files + obj_files

    if compiler_name == "cl":
        lib_command = [
            "lib",
            "/NOLOGO",
            f"/OUT:{output_name}",

        ] + object_files
    else:
        lib_command = [
            "ar",
            "rcs",
            output_name,
        ] + object_files

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

        FORMAT_PRINT(lib_command)
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
