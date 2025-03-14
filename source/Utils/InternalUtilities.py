import glob
import shutil
import sys

from source.Utils.ColorUtils import *
from source.Utils.MSVC_Utils import *
from source.Utils.TypesUtils import *
from source.Utils.DependencyUtils import *

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

def WARN_PRINT(msg):
    global indent_spaces
    color = YELLOW
    if msg:
        print(f"{color}{indent_spaces}{msg}{DEFAULT}")

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
    try:
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

    git_had_to_pull.append(True)

    cache_dir = os.getcwd()
    os.chdir(path)
    os.system(f"git reset --hard -q")
    os.system(f"git pull -q")
    os.chdir(cache_dir)

    return True

def PEEK_GIT_PULL():
    if len(git_had_to_pull) == 0:
        return False

    return git_had_to_pull[-1]

def CONSUME_GIT_PULL():
    if len(git_had_to_pull) == 0:
        return False

    return git_had_to_pull.pop()

def RESOLVE_FILE_GLOB(build_directory: str, maybe_source_glob: str, is_recursive: bool = False) -> List[str]:
    resolved_files = []

    os.makedirs(build_directory, exist_ok=True)

    if "*" not in maybe_source_glob:
        resolved_files.append(maybe_source_glob.replace("\\", "/"))
        return resolved_files

    if "*.cpp" in maybe_source_glob:
        extensions_to_check = ".cpp"
    elif "*.c" in maybe_source_glob:
        extensions_to_check = ".c"
    else:
        raise ValueError("Invalid input. Use '*.c', '*.cpp', or specify a single .c/.cpp file.")

    source_dir = os.path.dirname(maybe_source_glob) or "."
    original_directory = os.getcwd()

    def matches_extension(file_name: str) -> bool:
        return True if extensions_to_check in file_name else False

    try:
        os.chdir(build_directory)
        os.chdir(source_dir)

        if is_recursive:
            for root, _, files in os.walk(""):
                for file in files:
                    if matches_extension(file):
                        resolved_files.append(
                            os.path.join(source_dir, os.path.relpath(os.path.join(root, file))).replace("\\", "/")
                        )
        else:
            resolved_files.extend(
                os.path.join(source_dir, file).replace("\\", "/")
                for file in os.listdir("") if matches_extension(file)
            )
    finally:
        os.chdir(original_directory)

    return resolved_files