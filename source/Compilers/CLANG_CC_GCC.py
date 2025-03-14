from enum import Enum
from ..Procedure import Procedure
from ..UserUtilities import *

class CompilerAction(Enum):
    NO_ACTION = -1
    STD_VERSION = 0
    NO_LOGO = 1
    OBJECTS_ONLY = 2
    OUTPUT = 3
    COMPILE_TIME_DEFINES = 4
    MULTI_THREADING = 5
    ADDRESS_SANITIZER = 6
    WARNING_LEVEL = 7
    DISABLE_WARNINGS = 8
    DISABLE_SPECIFIC_WARNING = 9
    REPORT_FULL_PATH = 10
    DYNAMIC_LIB = 11
    WARNINGS_AS_ERRORS = 12

class CLANG_GCC_Compiler:
    def __init__(self, compiler_config: CompilerConfig):
        self.debug: bool = C_BUILD_IS_DEBUG()
        self.cc = compiler_config
        self.compiler_lookup_table: List[str] = [
            "-std=",              # STD_VERSION
            None,                 # NO_LOGO
            "-c",                 # OBJECT_FLAG
            "-o",                 # OUTPUT_FLAG
            "-D",                 # COMPILE_TIME_DEFINE_FLAG
            None,                 # MULTI_THREADING
            "-fsanitize=address", # ADDRESS_SANITIZER
            "-W",                 # WARNING_LEVEL
            "-w",                 # DISABLE_WARNINGS
            "-Wno-",              # DISABLE_SPECIFIC_WARNING
            None,                 # REPORT_FULL_PATH
            "-shared",            # DYNAMIC_LIB
            "-Werror"             # WARNINGS_AS_ERRORS
        ]

    def get_compiler_lookup(self, action: CompilerAction) -> str:
        return self.compiler_lookup_table[action.value]

    def compile_procedure(self, procedure: Procedure):
        build_directory = procedure.build_directory
        output_name = procedure.output_name
        source_files = procedure.source_files
        additional_libs = procedure.additional_libs
        compile_time_defines = procedure.compile_time_defines
        include_paths = procedure.include_paths

        self.cc.compiler_std_version = self.cc.compiler_std_version if self.cc.compiler_std_version else "c17"
        compiler_maybe_promoted_name = self.cc.compiler_name
        detected_cpp = False

        for source_name in source_files:
            if (".cpp" in source_name) or self.cc.compiler_name in ["g++", "clang++"]:
                detected_cpp = True
                self.cc.compiler_std_version = "c++20"
                if compiler_maybe_promoted_name == "gcc":
                    compiler_maybe_promoted_name = "g++"

                if compiler_maybe_promoted_name == "clang":
                    compiler_maybe_promoted_name = "clang++"

                break

        should_build_executable = False
        should_build_static_lib = False
        should_build_dynamic_lib = False

        extension: str = os.path.splitext(output_name)[-1].lower()
        if extension == ".exe":
            should_build_executable = True
        elif extension in [".lib", ".a"]:
            should_build_static_lib = True
        elif extension in [".so", ".o", ".dylib"]:
            should_build_dynamic_lib = True
        else:
            should_build_executable = True  # For Linux

        compiler_command: List[str] = [compiler_maybe_promoted_name]
        compiler_command.extend([source for source in source_files if source])

        # Add no logo flag
        no_logo_flag = self.get_compiler_lookup(CompilerAction.NO_LOGO)
        if no_logo_flag:
            compiler_command.append(no_logo_flag)

        # Add std version flag
        std_version_flags = self.get_compiler_lookup(CompilerAction.STD_VERSION)
        compiler_command.append(f"{std_version_flags}{self.cc.compiler_std_version}")

        report_full_path_flag = self.get_compiler_lookup(CompilerAction.REPORT_FULL_PATH)
        if report_full_path_flag:
            compiler_command.append(report_full_path_flag)

        # Add compile time defines
        compile_time_define_flag = self.get_compiler_lookup(CompilerAction.COMPILE_TIME_DEFINES)
        compiler_command.extend([f"{compile_time_define_flag}{define}" for define in compile_time_defines if define])

        # Add object flag
        if should_build_static_lib:
            object_flag = self.get_compiler_lookup(CompilerAction.OBJECTS_ONLY)
            compiler_command.append(object_flag)
        else:
            if should_build_dynamic_lib:
                dynamic_lib_flag = self.get_compiler_lookup(CompilerAction.DYNAMIC_LIB)
                compiler_command.append(dynamic_lib_flag)

            # Add output flag
            output_flag = self.get_compiler_lookup(CompilerAction.OUTPUT)
            compiler_command.append(output_flag)
            compiler_command.append(output_name)

        # Add multi-threading flag
        multi_threading_flag = self.get_compiler_lookup(CompilerAction.MULTI_THREADING)
        if multi_threading_flag:
            compiler_command.append(multi_threading_flag)

        # DISABLE ALL WARNINGS
        if self.cc.compiler_disable_warnings:
            disable_warnings_flag = self.get_compiler_lookup(CompilerAction.DISABLE_WARNINGS)
            compiler_command.append(disable_warnings_flag)

        # Add warning level flag
        if self.cc.compiler_warning_level and not self.cc.compiler_disable_warnings:
            warning_level_flag = self.get_compiler_lookup(CompilerAction.WARNING_LEVEL)
            compiler_command.append(f"{warning_level_flag}{self.cc.compiler_warning_level}")
        elif self.cc.compiler_warning_level and self.cc.compiler_disable_warnings:
            WARN_PRINT("Can't set warning level warnings are disabled. To re-enable this feature set compiler_disable_warnings = False")

        # Add disable specific warning flag
        disable_specific_warning_flag = self.get_compiler_lookup(CompilerAction.DISABLE_SPECIFIC_WARNING)
        if not self.cc.compiler_disable_warnings:
            for warning in self.cc.compiler_disable_specific_warnings:
                if warning:
                    compiler_command.append(f"{disable_specific_warning_flag}{warning}")
        elif len(self.cc.compiler_disable_specific_warnings) >= 1 and self.cc.compiler_disable_warnings:
            WARN_PRINT("Can't disable specific warnings because warnings are disabled. To re-enable this feature set compiler_disable_warnings = False")

        # Add warnings as errors flag
        if self.cc.compiler_treat_warnings_as_errors:
            warning_as_errors_flag = self.get_compiler_lookup(CompilerAction.WARNINGS_AS_ERRORS)
            compiler_command.append(warning_as_errors_flag)

        # Add optimization flag
        if self.debug:
            # Add address sanitizer flag
            if not self.cc.compiler_disable_sanitizer:
                address_sanitizer_flag = self.get_compiler_lookup(CompilerAction.ADDRESS_SANITIZER)
                compiler_command.append(address_sanitizer_flag)

            compiler_command.append("-g")
        else:
            compiler_command.append("-O2")

        # Add additional compiler args
        for arg in procedure.compiler_inject_into_args:
            if arg:
                compiler_command.append(arg)

        # Add include paths
        for include_path in include_paths:
            if include_path:
                compiler_command.append(f"-I{include_path}")

        if not should_build_static_lib:
            compiler_command.extend([lib for lib in additional_libs if lib])

        cached_current_directory = os.getcwd()
        try:
            if not os.path.exists(build_directory):
                os.mkdir(build_directory)
            os.chdir(build_directory)
            result = subprocess.run(compiler_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            for line in result.stdout.splitlines():
                NORMAL_PRINT(line.strip())

            for line in result.stderr.splitlines():
                NORMAL_PRINT(line.strip())

            FORMAT_PRINT(f"{compiler_command}")

            return_code = result.returncode
            if should_build_static_lib:
                build_static_lib(compiler_maybe_promoted_name, output_name, additional_libs)

            if return_code:
                FATAL_PRINT("FAILED TO COMPILE!")
                exit(return_code)
            else:
                FORMAT_PRINT(f"Compilation of {output_name} successful")

        finally:
            os.chdir(cached_current_directory)