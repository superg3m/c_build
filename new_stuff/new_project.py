import os
from distutils.command.build import build
from typing import List

from new_compiler import Compiler
from new_procedure import Procedure
from scripts.globals import FATAL_PRINT


class Project:
    def __init__(self, name, compiler_name, std_version = "c11", set_github_root = "https://github.com/superg3m"):
        self.name = name
        self.std_version = std_version
        self.set_github_root = set_github_root
        self.internal_compiler = Compiler(compiler_name)
        self.should_debug_with_visual_studio = False
        self.should_rebuild_project_dependencies = False
        self.dependencies = []
        self.procedures: List[Procedure] = []
        self.executable_procedures: List[Procedure] = []

    def set_executables_to_run(self, executable_names):
        executable_map = {}
        for proc in self.procedures:
            if proc:
                executable_map[proc.output_name] = proc

        for i in range(len(executable_names)):
            if executable_names[i] in executable_map.keys():
                self.executable_procedures.append(executable_map[executable_names[i]])
            else:
                FATAL_PRINT(f"Invalid executable name(s), expected: {executable_map.keys()} | got: {executable_names}")
                exit(-15)

    def add_procedure(self, build_directory):
        proc = Procedure(build_directory)
        self.procedures.append(proc)

        if not os.path.exists(build_directory):
            FATAL_PRINT(f"Can't find path at {build_directory}")
            exit(-15)

        return proc

    def inject_as_argument(self, arg):
        self.internal_compiler.compiler_arguments.append(arg)

    def set_project_dependencies(self, project_dependencies):
        for dependency in project_dependencies:
            self.dependencies.append(dependency)

    def set_rebuild_project_dependencies(self, should_rebuild_project_dependencies):
        self.should_rebuild_project_dependencies = should_rebuild_project_dependencies

    def set_debug_with_visual_studio(self, should_debug_with_visual_studio):
        self.should_debug_with_visual_studio = should_debug_with_visual_studio

    def set_compiler_warning_level(self, warning_level_string):
        self.internal_compiler.set_warning_level(warning_level_string)

    def disable_specific_warnings(self, specific_warnings):
        self.internal_compiler.disable_specific_warnings(specific_warnings)

    def set_treat_warnings_as_errors(self, is_error):
        self.internal_compiler.set_treat_warnings_as_errors(is_error)