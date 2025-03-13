# -------------------------------- GENERATED BY C_BUILD --------------------------------
from c_build.source.Utilities import *
from c_build.source.Manager import *
# --------------------------------------------------------------------------------------s

pc: ProjectConfig = ProjectConfig(
    project_name = "some_project",
    project_dependencies = [],
    project_debug_with_visual_studio = True,
    project_rebuild_project_dependencies = False,
    project_executable_procedures  = ["some_project.exe"]
)

cc: CompilerConfig = CompilerConfig(
    compiler_name = C_BUILD_COMPILER_NAME() if C_BUILD_IS_DEPENDENCY() else "INVALID_COMPILER",
    compiler_warning_level = [],
    compiler_disable_specific_warnings = False,
    compiler_treat_warnings_as_errors = True,
    compiler_disable_warnings  = False,
    compiler_disable_sanitizer = True
)

if IS_WINDOWS():
    cc.compiler_name = "cl"
if IS_DARWIN():
    cc.compiler_name = "clang"
elif IS_LINUX():
    cc.compiler_name = "gcc"

# Do different things depending on the platform
if cc.compiler_name == "cl":
    cc.compiler_warning_level = "3"
    cc.compiler_disable_specific_warnings = ["5105", "4668", "4820", "4996"]
else:
    cc.compiler_warning_level = "all"
    cc.compiler_disable_specific_warnings = ["deprecated", "parentheses"]

executable_procedure_libs = []
if IS_WINDOWS():
    windows_libs = ["User32.lib", "Gdi32.lib"] if cc.compiler_name == "cl" else ["-lUser32", "-lGdi32"]
    executable_procedure_libs += windows_libs

procedures_config = {
    "some_project_exe": ProcedureConfigElement(
        build_directory = f"./build_{cc.compiler_name}",
        output_name = "some_project.exe",
        source_files = ["../Source/*.c"],
        additional_libs = [],
        compile_time_defines = [],
        compiler_inject_into_args = [],
        include_paths = []
    ),
}

manager: Manager = Manager(cc, pc, procedures_config)
manager.build_project()
# -------------------------------------------------------------------------------------