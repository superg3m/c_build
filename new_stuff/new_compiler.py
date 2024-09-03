import constants
from constants import *
from scripts.globals import FATAL_PRINT

class Compiler:
    def __init__(self, compiler_name):
        self.name = compiler_name
        self.type = self.__choose_compiler_type()
        self.action = CompilerAction.NO_ACTION

        self.compiler_arguments = [self.name]

    def __choose_compiler_type(self):
        temp = CompilerType.INVALID
        if self.name == "cl":
            temp = CompilerType.CL
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
        self.compiler_arguments.append(f"{flag}{warning_level_string}")

    def disable_specific_warnings(self, specific_warnings):
        self.__set_action(CompilerAction.DISABLE_SPECIFIC_WARNING)
        flag = self.__get_compiler_lookup()
        for warning in specific_warnings:
            if warning:
                self.compiler_arguments.append(f"{flag}{warning}")

    def set_treat_warnings_as_errors(self, is_error):
        if not is_error:
            return
        self.__set_action(CompilerAction.WARNING_AS_ERRORS)
        flag = self.__get_compiler_lookup()
        self.compiler_arguments.append(f"{flag}")