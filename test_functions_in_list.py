from enum import Enum


class CompilerAction(Enum):
    STD_VERSION = 0
    NO_LOGO = 1

def check_version(version):
    return version == 6

funcs = print, check_version
args = ("Hello world!", ), (6, )

def set_up_action_table():
    return
    #arguments get resolved
    # functions are known as a constant

    # = [funcs, arguments]

for f, a, in zip(funcs, args):
    maybe_result = f(*a)
    if maybe_result:
        print(maybe_result)


# global
if compiler_type:
    self.compiler_type = compiler_type
else:
    self.compiler_type: str = compiler_json["compiler_type"]

self.compiler_type_enum = self.choose_compiler_type()
self.compiler_action: CompilerAction = CompilerAction.NO_ACTION

self.std_version: str = compiler_json["std_version"]
self.compiler_disable_warnings: bool = compiler_json["compiler_disable_warnings"]
self.compiler_warning_level: str = compiler_json["compiler_warning_level"]
self.compiler_treat_warnings_as_errors: bool = compiler_json["compiler_treat_warnings_as_errors"]
self.compiler_disable_specific_warnings: List[str] = compiler_json["disable_specific_warnings"]
self.compiler_inject_into_args = compiler_json["inject_as_argument"]
self.debug: bool = False

# procedure specific

# set up the action table
self.output_name: str = ""
self.build_directory: str = ""
self.compile_time_defines: List[str] = []
self.source_files: List[str] = []
self.include_paths: List[str] = []
self.additional_libs: List[str] = []
self.inject_into_args: List[str] = []
self.should_build_executable: bool = False
self.should_build_static_lib: bool = False
self.should_build_dynamic_lib: bool = False

self.compiler_arguments = ""