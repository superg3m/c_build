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

        wrong_dependency_format = []
        for dependency in self.pc.project_dependencies:
            if not isinstance(dependency, Dependency):
                wrong_dependency_format.append(dependency)

        if len(wrong_dependency_format) > 0:
            FATAL_PRINT(f"ProjectName: {pc.project_name}\n"
                        f"DependencyNames: {wrong_dependency_format}\n"
                        f"ErrorMessage: 'DependencyNames are not of type 'Dependency' they are likely just strings")
            exit(-1)

    def serialize_to_json(self):
        serialized_name = f"c_build_dependency_cache_{C_BUILD_COMPILER_NAME()}_{C_BUILD_BUILD_TYPE()}.json"

        for dependency in self.pc.project_dependencies:
            dependency.always_pull = C_BUILD_ALWAYS_PULL()
            print(dependency.always_pull)
            print(C_BUILD_ALWAYS_PULL())

        filtered_procedure_config = {}
        for key, value in self.procedures.items():
            filtered_procedure_config[key] = value.to_dict()

        serialized_data = {
            **self.pc.to_dict(),
            **filtered_procedure_config
        }

        with open(serialized_name, "w") as file:
            json.dump(serialized_data, fp=file, indent=4,  default=lambda o: o.__dict__)

        return json.dumps(serialized_data, indent=4, default=lambda o: o.__dict__)

    def build_project(self):
        if C_BUILD_IS_DEPENDENCY():
            self.serialize_to_json()
            return

        execution_type = C_BUILD_EXECUTION_TYPE()
        if execution_type == "BUILD":
            if self.pc.project_rebuild_project_dependencies:
                WARN_PRINT(f"Forcing recompile because project_rebuild_project_dependencies")
            else:
                sanitizer_enabled_and_debug = not self.INTERNAL_COMPILER.compiler_disable_sanitizer and C_BUILD_BUILD_TYPE() == "debug"
                if sanitizer_enabled_and_debug:
                    WARN_PRINT(f"Forcing recompile because sanitizer_enabled_and_debug")

        project = Project(self.INTERNAL_COMPILER, self.pc, self.procedures)
        project.build()
