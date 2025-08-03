from .Utils.DependencyUtils import *
from .Utils.ColorUtils import *
from .Utils.PlatformUtils import *
from .Utils.TypesUtils import *

def GET_LIB_NAME(cc: CompilerConfig, lib_name: str) -> str:
    return f"{lib_name}.lib" if cc.compiler_name == "cl" else f"lib{lib_name}.a"

def GET_LIB_FLAG(cc: CompilerConfig, lib_name: str) -> str:
    return f"{lib_name}.lib" if cc.compiler_name == "cl" else f"-l{lib_name}"


def COPY_FILE_TO_DIR(src_directory: str, file_name: str, destination_directory: str):
    if not os.path.exists(f"{destination_directory}/{file_name}"):
        import shutil
        shutil.copy(f"{src_directory}/{file_name}", destination_directory)