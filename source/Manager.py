import json

from .Compilers.CLANG_GCC import *
from .Compilers.MSVC_CL import *

from .Project import Project
from .Utilities import (C_BUILD_IS_DEPENDENCY, SET_MSVC_VARS_FROM_CACHE, C_BUILD_COMPILER_NAME, IS_PULL_REQUIRED)
class Manager:
    def __init__(self, compiler_config, project_config, procedures_config):
        self.INTERNAL_COMPILER = None
        if C_BUILD_COMPILER_NAME() == "cl":
            self.INTERNAL_COMPILER = MSVC_CL_Compiler(compiler_config)
            SET_MSVC_VARS_FROM_CACHE()
        if C_BUILD_COMPILER_NAME() in ["gcc", "clang", "g++", "clang++"]:
            self.INTERNAL_COMPILER = CLANG_GCC_Compiler(compiler_config)

        self.project_config = project_config
        self.procedures_config = procedures_config

    def build_project(self):
        serialized_name = f"c_build_dependency_cache_{C_BUILD_COMPILER_NAME()}.json"
        for dependency_name in self.project_config["project_dependencies"]:
            if dependency_name and os.path.exists(f"./{dependency_name}"):
                if os.path.exists(f"./{dependency_name}/{serialized_name}") and IS_PULL_REQUIRED(dependency_name):
                    os.remove(f"./{dependency_name}/{serialized_name}")

        if C_BUILD_IS_DEPENDENCY():
            filtered_project_config = self.project_config.copy()
            filtered_project_config.pop("project_debug_with_visual_studio", None)
            serialized_data = {
                **filtered_project_config,
                **self.procedures_config
            }
            with open(serialized_name, "w") as file:
                json.dump(serialized_data, file, indent=4)
            return


        project = Project(self.INTERNAL_COMPILER, self.project_config, self.procedures_config)
        project.build()