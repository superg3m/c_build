import os
from typing import Dict

import constants
from constants import *
from vc_vars import *
from globals import FATAL_PRINT, NORMAL_PRINT, FORMAT_PRINT, build_static_lib

std_version_default = "c11"

class Compiler:
    def __init__(self, compiler_name, std_version):
        self.name = compiler_name
        self.std_version = std_version
        self.should_debug_with_visual_studio = False
        self.should_rebuild_project_dependencies = False
        self.should_rebuild_project_dependencies = False
        self.should_rebuild_project_dependencies = False
        self.should_rebuild_project_dependencies = False
        self.type = self.__choose_compiler_type()
        self.compiler_command = [self.name]

    def __choose_compiler_type(self):
        temp = CompilerType.INVALID
        if self.name == "cl":
            temp = CompilerType.CL
            generate_vars_file_cache()
            set_vs_vars_from_file()
        elif self.name in ["gcc", "cc", "clang"]:
            temp = CompilerType.GCC_CC_CLANG
        else:
            FATAL_PRINT(f"Compiler {self.name} is not supported")
            exit(-15)
        return temp

    def __get_compiler_lookup(self):
        if self.action == CompilerAction.NO_ACTION:
            FATAL_PRINT(f"Compiler No Action")
            exit(-15)
        return constants.compiler_lookup_table[self.type.value][self.action.value]

    def __set_action(self, action: CompilerAction):
        self.action = action

    def set_warning_level(self, warning_level_string):
        self.__set_action(CompilerAction.WARNING_LEVEL)
        flag = self.__get_compiler_lookup()
        self.compiler_command.append(f"{flag}{warning_level_string}")

    def disable_specific_warnings(self, specific_warnings):
        self.__set_action(CompilerAction.DISABLE_SPECIFIC_WARNING)
        flag = self.__get_compiler_lookup()
        for warning in specific_warnings:
            if warning:
                self.compiler_command.append(f"{flag}{warning}")

    def set_treat_warnings_as_errors(self, is_error):
        if not is_error:
            return
        self.__set_action(CompilerAction.WARNING_AS_ERRORS)
        flag = self.__get_compiler_lookup()
        self.compiler_command.append(f"{flag}")

    def set_compile_time_defines(self, compile_time_defines):
        self.__set_action(CompilerAction.COMPILE_TIME_DEFINES)
        compile_time_define_flag = self.__get_compiler_lookup()
        for define in compile_time_defines:
            if define:
                self.compiler_command.append(f"{compile_time_define_flag}{define}")



    def compile_procedure(self, procedure, is_debug = False):
        for source in procedure.source_files:
            if source:
                self.compiler_command.append(source)

        # Add no logo flag
        self.__set_action(CompilerAction.NO_LOGO)
        no_logo_flag = self.__get_compiler_lookup()
        if no_logo_flag:
            self.compiler_command.append(no_logo_flag)

        # Add std version flag
        self.__set_action(CompilerAction.STD_VERSION)
        std_version_flag = self.__get_compiler_lookup()
        self.compiler_command.append(f"{std_version_flag}{self.std_version}")

        # add full report
        self.__set_action(CompilerAction.REPORT_FULL_PATH)
        report_full_path_flag = self.__get_compiler_lookup()
        if report_full_path_flag:
            self.compiler_command.append(report_full_path_flag)

        # Add object flag
        if procedure.should_build_static_lib:
            self.__set_action(CompilerAction.OBJECTS_ONLY)
            object_flag = self.__get_compiler_lookup()
            self.compiler_command.append(object_flag)
        else:
            if procedure.should_build_dynamic_lib:
                dynamic_lib_flag = self.__get_compiler_lookup()
                if self.name == "cl":
                    self.compiler_command.append("/LD")  # Use CL-specific flag for dynamic libraries
                else:
                    self.compiler_command.append("-shared")  # Use common flag for GCC/CC/CLANG

            # Add output flag
            self.__set_action(CompilerAction.OUTPUT)
            output_flag = self.__get_compiler_lookup()
            self.compiler_command.append(output_flag)
            self.compiler_command.append(procedure.output_name)

        # Add multi-threading flag
        self.__set_action(CompilerAction.MULTI_THREADING)
        multi_threading_flag = self.__get_compiler_lookup()
        if multi_threading_flag:
            self.compiler_command.append(multi_threading_flag)


        # Add optimization flag
        if is_debug:
            # Add address sanitizer flag
            if os.name != 'nt':
                self.__set_action(CompilerAction.ADDRESS_SANITIZER)
                address_sanitizer_flag = self.__get_compiler_lookup()
                self.compiler_command.append(address_sanitizer_flag)

            if self.type == CompilerType.CL:
                self.compiler_command.append("/Od")
                self.compiler_command.append("/Zi")
            else:
                self.compiler_command.append("-g")
        else:
            if self.type == CompilerType.CL:
                self.compiler_command.append("/O2")
            else:
                self.compiler_command.append("-O2")

        # Add include paths
        for include_path in procedure.include_paths:
            if include_path:
                if self.type == CompilerType.CL:
                    self.compiler_command.append(f"/I{include_path}")
                else:
                    self.compiler_command.append(f"-I{include_path}")

        # Add additional compiler flags
        #for flag in procedure.compiler_inject_into_args:
            #if flag:
                #self.compiler_command.append(flag)

        if not procedure.should_build_static_lib:
            if len(procedure.additional_libs) > 0 and procedure.additional_libs[0] and self.type == CompilerType.CL:
                self.compiler_command.append("/link")
            for lib in procedure.additional_libs:
                if lib:
                    self.compiler_command.append(lib)

        cached_current_directory = os.getcwd()
        error_occurred = False
        return_code = 0

        try:
            if not os.path.exists(procedure.build_directory):
                os.mkdir(procedure.build_directory)
            os.chdir(procedure.build_directory)
            result = subprocess.run(self.compiler_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            for line in result.stdout.splitlines():
                NORMAL_PRINT(line.strip())

            for line in result.stderr.splitlines():
                NORMAL_PRINT(line.strip())

            FORMAT_PRINT(f"{self.compiler_command}")

            if procedure.should_build_static_lib:
                if build_static_lib(procedure.compiler_type, procedure.output_name, procedure.additional_libs):
                    FATAL_PRINT(f"FAILED TO COMPILE LIB: {procedure.output_name}")
                    error_occurred = True
            elif return_code:
                FATAL_PRINT("FAILED TO COMPILE!")
                error_occurred = True
            else:
                FORMAT_PRINT(f"Compilation of {procedure.output_name} successful")

            return_code = result.returncode
        finally:
            os.chdir(cached_current_directory)