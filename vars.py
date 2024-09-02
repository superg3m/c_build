import os
import subprocess
import time
from typing import List, Set

file_name: str = "c_build_cl_vars_cache.txt"

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
        return ""

    command = f'cmd.exe /c set'
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    original_set = set(result.stdout.splitlines());

    vcvarsall_path = os.path.join(vs_path, "VC", "Auxiliary", "Build", "vcvarsall.bat")
    command = f'cmd.exe /c "call \"{vcvarsall_path}\" x64 > nul && set"'
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    new_set = set(result.stdout.splitlines())

    if result.returncode != 0:
        #FATAL_PRINT("Failed to set Visual Studio environment.")
        exit(-12)
        return ""

    return_set = new_set.difference(original_set)

    return list(return_set)

def generate_vars_file_cache():
    if os.path.exists(file_name):
        return

    lines_to_write = get_vs_environment()

    with open(file_name, "w") as generated_file:
        for line in lines_to_write:
            generated_file.write(line + "\n")



def set_vs_vars_from_file():
    if is_cl_in_path():
        return ""

    with open(file_name, "r") as file:
        for line in file.readlines():
            if "=" in line:
                name, value = line.strip().split("=", 1)
                os.environ[name] = value

if __name__ == "__main__":
    start_time = time.perf_counter()
    generate_vars_file_cache()
    set_vs_vars_from_file()
    os.system("cl")
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"|--------------- Time elapsed: {elapsed_time:.2f} seconds ---------------|")