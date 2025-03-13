import json

from .Compilers.CLANG_CC_GCC import *
from .Compilers.MSVC_CL import *
from .Project import Project
from .Utilities import *

class Manager:
    def __init__(self, compiler_config: CompilerConfig, project_config: ProjectConfig, procedures_config: dict[str, ProcedureConfigElement]):
        self.INTERNAL_COMPILER = None
        if compiler_config.compiler_name == "cl":
            self.INTERNAL_COMPILER = MSVC_CL_Compiler(compiler_config)
            SET_MSVC_VARS_FROM_CACHE()
        elif compiler_config.compiler_name in ["cc", "gcc", "g++", "clang", "clang++"]:
            self.INTERNAL_COMPILER = CLANG_GCC_Compiler(compiler_config)
        else:
            FATAL_PRINT(f"Unsupported Compiler: {compiler_config.compiler_name}\nSupported Compilers: [cl, cc, gcc, g++, clang, clang++]")
            exit(-1)

        self.project_config = project_config
        self.procedures_config = procedures_config

    def build_project(self):
        serialized_name = f"c_build_dependency_cache_{C_BUILD_COMPILER_NAME()}.json"
        for dependency_name in self.project_config.project_dependencies:
            if dependency_name and os.path.exists(f"./{dependency_name}"):
                if os.path.exists(f"./{dependency_name}/{serialized_name}") and IS_PULL_REQUIRED(dependency_name):
                    os.remove(f"./{dependency_name}/{serialized_name}")

        if C_BUILD_IS_DEPENDENCY():
            filtered_project_config = self.project_config.__dict__.copy()
            filtered_project_config.pop("project_debug_with_visual_studio", None)

            FATAL_PRINT(**self.procedures_config.__dict__)

            serialized_data = {
                **filtered_project_config,
                **self.procedures_config.__dict__
            }
            with open(serialized_name, "w") as file:
                json.dump(serialized_data, file, indent=4)
            return

        project = Project(self.INTERNAL_COMPILER, self.project_config, self.procedures_config)
        project.build()