import copy
import glob
import os
import shutil
import subprocess
import sys
from typing import List

from .ColorUtils import *
from .TypesUtils import *
from .DependencyUtils import *
from .PlatformUtils import *

level = 0
indent_spaces = " " * (level * 4)


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


def FORMAT_PRINT(msg, end="\n", should_indent=True):
    global indent_spaces
    canonical_indent = indent_spaces if should_indent else ""
    color_lookup = [GREEN, BLUE, YELLOW, MAGENTA, CYAN, RED]
    color = color_lookup[level % len(color_lookup)]
    if msg:
        print(f"{color}{canonical_indent}{msg}{DEFAULT}", end=end)


def NORMAL_PRINT(msg):
    global indent_spaces
    if msg:
        print(f"{indent_spaces}{msg}")


def WARN_PRINT(msg):
    global indent_spaces
    if msg:
        print(f"{WARN_YELLOW}{indent_spaces}[WARN]: {msg}{DEFAULT}")


def FATAL_PRINT(msg):
    global indent_spaces
    if msg:
        print(f"{FATAL}{indent_spaces}[FATAL]: {msg}{DEFAULT}")


def IS_WINDOWS_PROCESS_RUNNING(process_name):
    programs = str(subprocess.check_output('tasklist'))
    if process_name in programs:
        return True
    else:
        return False


def build_static_lib(compiler_name, output_name, additional_libs):
    lib_command = []

    o_files = glob.glob('*.o')
    obj_files = glob.glob('*.obj')
    object_files = o_files + obj_files

    if compiler_name == "cl":
        lib_command = [
                          "lib",
                          "/NOLOGO",
                          f"/OUT:{output_name}",
                      ] + object_files
    elif sys.platform == 'darwin':
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
    result = None
    try:
        if shutil.which(lib_command[0]) is None:
            raise FileNotFoundError(f"{lib_command[0]} command not found")

        result = subprocess.run(lib_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        FORMAT_PRINT(f'; {" ".join(lib_command)}', end="", should_indent=False)
    except FileNotFoundError:
        FATAL_PRINT(f"{lib_command[0]} command not found")
        error_occurred = True
    except subprocess.CalledProcessError as e:
        WARN_PRINT(f"======= Error: static lib failed with return code {e.returncode} =======")
        if e.stdout:
            error_lines = e.stdout.splitlines()
            for line_2 in error_lines:
                if line_2.strip() and not line_2.endswith(".c"):
                    FATAL_PRINT(f"Compilation error | {line_2.strip()}")

        NORMAL_PRINT(f"Lib Command: {e.cmd}")
        WARN_PRINT(f"==========================================================================")
        error_occurred = True
    finally:
        for line_2 in result.stdout.splitlines():
            NORMAL_PRINT(line_2.strip())

        for line_2 in result.stderr.splitlines():
            NORMAL_PRINT(line_2.strip())

        if error_occurred:
            FATAL_PRINT(f"FAILED TO COMPILE LIB: {output_name}")


def IS_PULL_REQUIRED(path: str) -> bool:
    original_dir = os.getcwd()
    try:
        os.chdir(path)
        subprocess.run(["git", "fetch", "-q"])
        output = subprocess.run(["git", "status"], capture_output=True, text=True, check=True)
        lines = output.stdout.splitlines()

        for line in lines:
            if any(keyword in line for keyword in ["Your branch is behind", "have diverged"]):
                return True

    finally:
        os.chdir(original_dir)

    return False


git_had_to_pull = []


def GIT_PULL(path: str) -> bool:
    global git_had_to_pull

    if not IS_PULL_REQUIRED(path):
        git_had_to_pull.append(False)
        return False

    cache_dir = os.getcwd()
    os.chdir(path)
    os.system(f"git reset --hard -q")
    os.system(f"git pull -q")
    os.chdir(cache_dir)

    git_had_to_pull.append(True)
    return True


def GIT_HAS_PULL():
    for pull in git_had_to_pull:
        if pull:
            return True

    return False


def RESOLVE_FILE_GLOB(build_directory: str, maybe_source_glob: str) -> list[str]:
    resolved_files = []
    os.makedirs(build_directory, exist_ok=True)

    extension = ".INVALID"
    is_recursive = "/**/" in maybe_source_glob
    source_dir = ""
    source_file_name = ""

    if is_recursive:
        source_pair = maybe_source_glob.split("/**/")
        if len(source_pair) > 2 or "/**/**/" in maybe_source_glob:
            FATAL_PRINT(f"Invalid Source: {maybe_source_glob} | two or more '/**/' present")
            exit(-1)

        source_dir = source_pair[0]
        source_file_name = source_pair[1]
    else:
        source_dir = os.path.dirname(maybe_source_glob) or "."
        source_file_name = os.path.basename(maybe_source_glob)

    if "*.cpp" in maybe_source_glob:
        extension = ".cpp"
        using_wildcard = True
    elif "*.c" in maybe_source_glob:
        extension = ".c"
        using_wildcard = True
    elif ".cpp" in maybe_source_glob:
        extension = ".cpp"
        using_wildcard = False
    elif ".c" in maybe_source_glob:
        extension = ".c"
        using_wildcard = False
    else:
        raise ValueError("Invalid input. Use '*.c', '*.cpp', or specify a single .c/.cpp file.")

    if not is_recursive and not using_wildcard:
        resolved_files.append(maybe_source_glob.replace("\\", "/"))
        return resolved_files

    def matches_pattern(file_name: str) -> bool:
        return (file_name.endswith(extension) and using_wildcard) or file_name == source_file_name

    original_directory = os.getcwd()
    try:
        os.chdir(build_directory)
        os.chdir(source_dir)
        if is_recursive:
            for root, _, files in os.walk("."):
                for file in files:
                    if matches_pattern(file):
                        file_path = os.path.join(source_dir, os.path.relpath(os.path.join(root, file)))
                        resolved_files.append(file_path.replace("\\", "/"))
        else:
            for file in os.listdir("."):
                if matches_pattern(file):
                    file_path = os.path.join(source_dir, file)
                    resolved_files.append(file_path.replace("\\", "/"))
    finally:
        os.chdir(original_directory)

    return resolved_files


MSVC_CACHED_NAME: str = "./c_build/source/c_build_cl_vars_cache.txt"


def find_vs_path() -> str:
    vswhere_path = r"C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe"
    result = subprocess.run(
        [vswhere_path, "-latest", "-requires", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64", "-property",
         "installationPath"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        return result.stdout.strip()
    else:
        FATAL_PRINT("Could not find Visual Studio installation path.")
        exit(-1)


def is_cl_in_path():
    for path in os.environ.get("PATH", "").split(os.pathsep):
        if os.path.isfile(os.path.join(path, "cl.exe")) and os.path.isfile(os.path.join(path, "lib.exe")):
            return True
    return False


def get_vs_environment():
    vs_path = find_vs_path()
    if not vs_path:
        FATAL_PRINT("Visual Studio not found.")
        exit(-1)

    command = f'cmd.exe /c set'
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    original_set = set(result.stdout.splitlines())

    vcvarsall_path = os.path.join(vs_path, "VC", "Auxiliary", "Build", "vcvarsall.bat")
    command = f'cmd.exe /c "call \"{vcvarsall_path}\" x64 > nul && set"'
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    new_set = set(result.stdout.splitlines())

    if result.returncode != 0:
        FATAL_PRINT("Failed to set Visual Studio environment.")
        exit(-12)

    return_set = new_set.difference(original_set)

    return list(return_set)


def generate_vars_file_cache():
    if os.path.exists(MSVC_CACHED_NAME):
        return

    print("CWD PATH: ", os.getcwd())

    lines_to_write = get_vs_environment()
    if len(lines_to_write) == 0:
        FATAL_PRINT("Failed to generate vcvars cache because failed to get vs env")
        exit(-1)

    with open(MSVC_CACHED_NAME, "w") as generated_file:
        for line in lines_to_write:
            generated_file.write(line + "\n")


def SET_MSVC_VARS_FROM_CACHE():
    # If you already have cl in path, and you didn't generate a cache
    # then you are in trouble...
    if is_cl_in_path():
        return

    print("Got here")

    generate_vars_file_cache()
    try:
        with open(MSVC_CACHED_NAME, "r") as file:
            for line in file.readlines():
                if "=" in line:
                    name, value = line.strip().split("=", 1)
                    os.environ[name] = value
    except IOError as e:
        FATAL_PRINT(f"Failed to open vscache, Error: {e}")
        exit(-1)
