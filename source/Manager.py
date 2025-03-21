from .Compilers.CLANG_CC_GCC import *
from .Compilers.MSVC_CL import *
from .Project import Project
from .Utils.InternalUtilities import SET_MSVC_VARS_FROM_CACHE, FATAL_PRINT, VALID_COMPILERS, GIT_PULL

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

    def serialize_to_json(self):
        serialized_name = f"c_build_dependency_cache_{C_BUILD_COMPILER_NAME()}.json"
        filtered_project_config = self.project_config.to_dict()
        filtered_procedure_config = {}
        for key, value in self.procedures_config.items():
            filtered_procedure_config[key] = value.to_dict()

        serialized_data = {
            **filtered_project_config,
            **filtered_procedure_config
        }

        with open(serialized_name, "w") as file:
            json.dump(serialized_data, file, indent=4)

    def build_project(self):
        if C_BUILD_IS_DEPENDENCY():
            self.serialize_to_json()
            return

        project = Project(self.INTERNAL_COMPILER, self.project_config, self.procedures_config)
        project.build()