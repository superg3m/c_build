import argparse
import asyncio
import glob
import os
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

level = 0
indent_spaces = " " * (level * 4)
parser = argparse.ArgumentParser()
parser.add_argument('--build_type', default="debug", type=str, required=False, help='build_type -> { debug, release }')
parser.add_argument('--is_dependency', default="false", type=str, required=False, help='is_dependency -> { true, false }')
parser.add_argument('--execution_type', default="BUILD", type=str, required=False, help='Build type -> { BUILD, RUN, CLEAN, DEBUG }')
parser.add_argument('--compiler_name', default="cl", type=str, required=False, help='Compiler Name -> { cl, gcc, cc, clang }')

def __IS_PULL_REQRUIED(path: str) -> bool:
    cache_dir = os.getcwd()
    os.chdir(path)
    os.system(f"git fetch -q")
    p = subprocess.Popen(["git", "status"], stdout=subprocess.PIPE, stderr = subprocess.PIPE)
    out, err = p.communicate()
    lines = out.splitlines()
    os.chdir(cache_dir)

    if "Your branch is behind" in lines or "have diverged" in lines:
        return True
    elif "Changes not staged for commit" in lines or "Untracked files" in lines:
        return True

    return False

git_had_to_pull = []
def GIT_PULL(path: str):
    global git_had_to_pull
    if not __IS_PULL_REQRUIED(path):
        return

    git_had_to_pull.append(True)
    FATAL_PRINT(f"ARR: {git_had_to_pull}")

    cache_dir = os.getcwd()
    os.chdir(path)
    os.system(f"git reset --hard origin/main -q")

    os.system(f"git reset --hard origin/main -q")
    os.system(f"git pull -q")
    os.chdir(cache_dir)

def CHECK_AND_CONSUME_GIT_PULL():
    if len(git_had_to_pull) == 0:
        return False

    FATAL_PRINT(f"ARR: {git_had_to_pull}")
    return git_had_to_pull.pop()

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

def IS_WINDOWS_PROCESS_RUNNING(process_name):
    programs = str(subprocess.check_output('tasklist'))
    if process_name in programs:
        return True
    else:
        return False

MSVC_CACHED_NAME: str = "./c_build/source/c_build_cl_vars_cache.txt"

def find_vs_path() -> str:
    vswhere_path = r"C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe"
    result = subprocess.run(
        [vswhere_path, "-latest", "-requires", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64", "-property", "installationPath"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        return result.stdout.strip()
    else:
        # FORMAT_PRINT("Could not find Visual Studio installation path.")
        exit(-1)

def is_cl_in_path():
    for path in os.environ.get("PATH", "").split(os.pathsep):
        if os.path.isfile(os.path.join(path, "cl.exe")) and os.path.isfile(os.path.join(path, "lib.exe")):
            return True
    return False

def get_vs_environment():
    vs_path = find_vs_path()
    if not vs_path:
        # FATAL_PRINT("Visual Studio not found.")
        exit(-1)

    command = f'cmd.exe /c set'
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    original_set = set(result.stdout.splitlines())

    vcvarsall_path = os.path.join(vs_path, "VC", "Auxiliary", "Build", "vcvarsall.bat")
    command = f'cmd.exe /c "call \"{vcvarsall_path}\" x64 > nul && set"'
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    new_set = set(result.stdout.splitlines())

    if result.returncode != 0:
        #FATAL_PRINT("Failed to set Visual Studio environment.")
        exit(-12)

    return_set = new_set.difference(original_set)

    return list(return_set)

def generate_vars_file_cache():
    if os.path.exists(MSVC_CACHED_NAME):
        return

    lines_to_write = get_vs_environment()

    with open(MSVC_CACHED_NAME, "w") as generated_file:
        for line in lines_to_write:
            generated_file.write(line + "\n")

def SET_MSVC_VARS_FROM_CACHE():
    if is_cl_in_path():
        return ""

    generate_vars_file_cache()
    with open(MSVC_CACHED_NAME, "r") as file:
        for line in file.readlines():
            if "=" in line:
                name, value = line.strip().split("=", 1)
                os.environ[name] = value

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
    elif compiler_name in ["gcc", "cc", "clang"] and sys.platform == 'darwin':
        lib_command = [
          "libtool",
          "-static",
          "-o",
          output_name,
        ] + object_files
    else:
        lib_command = [
          "ar",
          "rcs",
          output_name,
        ] + object_files

    lib_command.extend([lib for lib in additional_libs if lib])
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
            FATAL_PRINT(f"FAILED TO COMPILE LIB: {output_name}")
            sys.exit(-1)

# either release or debug
def C_BUILD_IS_DEBUG():
    return parser.parse_args().build_type == "debug"

def C_BUILD_COMPILER_NAME():
    return parser.parse_args().compiler_name

def C_BUILD_IS_DEPENDENCY():
    return parser.parse_args().is_dependency == "true"

def C_BUILD_EXECUTION_TYPE():
    return parser.parse_args().execution_type

def C_BUILD_LIB(lib_name, compiler_name):
    return f"{lib_name}.lib" if compiler_name == "cl" else f"lib{lib_name}.a"

def IS_WINDOWS():
    return os.name == "nt"

def IS_LINUX():
    return os.name == "posix" and os.uname().sysname == "Linux"

def IS_DARWIN():
    return os.name == "posix" and os.uname().sysname == "Darwin"


def RESOLVE_FILE_GLOB(self, maybe_source_glob: str, is_recursive: bool) -> List[str]:
    resolved_files = []

    if '*.c' in maybe_source_glob:
        source_dir = os.path.dirname(maybe_source_glob) or "."
        current_directory = os.getcwd()

        try:
            os.chdir(self.build_directory)
            os.chdir(source_dir)

            if is_recursive:
                for root, _, files in os.walk(os.getcwd()):
                    for file in files:
                        if file.endswith('.c'):
                            relative_path = source_dir + "/" + os.path.relpath(os.path.join(root, file)).replace("\\", "/")
                            resolved_files.append(relative_path)
            else:

                for file in os.listdir(os.getcwd()):
                    if file.endswith('.c'):
                        relative_path = os.path.join(source_dir, file).replace("\\", "/")
                        resolved_files.append(relative_path)
        finally:
            os.chdir(current_directory)

    elif '.c' in maybe_source_glob:
        resolved_files.append(maybe_source_glob)

    return resolved_files