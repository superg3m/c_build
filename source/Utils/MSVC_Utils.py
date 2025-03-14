import os
import subprocess

from source.InternalUtilities import FATAL_PRINT

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