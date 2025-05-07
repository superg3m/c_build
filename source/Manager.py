from copyreg import constructor

import jsonpickle

from typing import Dict

from .Compilers.CLANG_CC_GCC import *
from .Compilers.MSVC_CL import *
from .Project import Project
from .Utils.InternalUtilities import SET_MSVC_VARS_FROM_CACHE, FATAL_PRINT, VALID_COMPILERS, GIT_PULL

def choose_internal_compiler(cc: CompilerConfig):
    if cc.compiler_name == "cl":
        SET_MSVC_VARS_FROM_CACHE()
        return MSVC_CL_Compiler(cc)
    elif cc.compiler_name in ["cc", "gcc", "g++", "clang", "clang++"]:
        return CLANG_GCC_Compiler(cc)
    else:
        FATAL_PRINT(f"Unsupported Compiler: {cc.compiler_name}")
        FATAL_PRINT(f"Supported Compilers: [cl, cc, gcc, g++, clang, clang++]")
        exit(-1)


class Manager:
    def __init__(self, cc: CompilerConfig, pc: ProjectConfig, procedures: Dict[str, ProcedureConfig]):
        self.pc: ProjectConfig = pc
        self.procedures: Dict[str, ProcedureConfig] = procedures
        self.INTERNAL_COMPILER = choose_internal_compiler(cc)

    def serialize_to_json(self):
        serialized_name = f"c_build_dependency_cache_compiler_build_type.json"  # You may want to pass in these values

        filtered_procedure_config = {}
        for key, value in self.procedures.items():
            filtered_procedure_config[key] = value.to_dict()


        serialized_data = {
            **filtered_procedure_config
        }

        print(self.pc.to_json())

        exit(-1)

        """
        with open(serialized_name, "w") as file:
            json.dump(jsonpickle.encode(serialized_data), file, indent=4)
        """
        return json.dumps(serialized_data, indent=4)

    def build_project(self):
        if C_BUILD_IS_DEPENDENCY():
            self.serialize_to_json()
            return

        project = Project(self.INTERNAL_COMPILER, self.pc, self.procedures)
        project.build()
