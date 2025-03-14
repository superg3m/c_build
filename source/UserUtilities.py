from .Utils.DependencyUtils import *
from .Utils.ColorUtils import *
from .Utils.PlatformUtils import *
from .Utils.TypesUtils import *

def GET_LIB_FILENAME(cc: CompilerConfig, lib_name: str) -> str:
    return f"{lib_name}.lib" if cc.compiler_name == "cl" else f"lib{lib_name}.a"

def GET_LIB_FLAG(cc: CompilerConfig, lib_name: str) -> str:
    return f"{lib_name}.lib" if cc.compiler_name == "cl" else f"-l{lib_name}"