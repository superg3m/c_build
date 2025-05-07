import json
from enum import Enum
from typing import List, Optional, Dict, Any
VALID_COMPILERS = ["cl", "gcc", "g++", "cc", "clang", "clang++"]

GITHUB_ALWAYS_PULL = 0
GITHUB_NEVER_PULL = 1

class Dependency:
    def __init__(self, name: str, host: str = "https://github.com/superg3m", branch_name: str = "main", always_pull: bool = True):
        self.name: str = name
        self.host: str = host
        self.branch_name: str = branch_name
        self.always_pull: bool = always_pull

    def __repr__(self):
        json.dumps(self.__dict__, indent=4)

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_json(cls, dictionary):
        def decoder(obj) -> Dependency:
            return Dependency(**obj)

        return json.loads(dictionary, object_hook=decoder)


class ProjectConfig:
    def __init__(self, project_name: str, project_dependencies: Optional[List[Dependency]] = None,
                 project_debug_with_visual_studio: bool = True, project_rebuild_project_dependencies: bool = False,
                 project_executable_names: Optional[List[str]] = None):
        self.project_name: str = project_name
        self.project_dependencies: List[Dependency] = project_dependencies or []
        self.project_debug_with_visual_studio: bool = project_debug_with_visual_studio
        self.project_rebuild_project_dependencies: bool = project_rebuild_project_dependencies
        self.project_executable_names: List[str] = project_executable_names or []

    def __repr__(self):
        json.dumps(self.__dict__, indent=4)

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_json(cls, dictionary):
        def decoder(obj) -> ProjectConfig:
            return ProjectConfig(**obj)

        return json.loads(dictionary, object_hook=decoder)

class CompilerConfig:
    def __init__(self, compiler_name: str, compiler_std_version: str = "c11",
                 compiler_warning_level: str = "", compiler_disable_specific_warnings: Optional[list[str]] = None,
                 compiler_treat_warnings_as_errors: bool = True, compiler_disable_warnings: bool = False,
                 compiler_disable_sanitizer: bool = True):
        self.compiler_name: str = compiler_name
        self.compiler_std_version: str = compiler_std_version
        self.compiler_warning_level: str = compiler_warning_level
        self.compiler_disable_specific_warnings: list[str] = compiler_disable_specific_warnings or []
        self.compiler_treat_warnings_as_errors: bool = compiler_treat_warnings_as_errors
        self.compiler_disable_warnings: bool = compiler_disable_warnings
        self.compiler_disable_sanitizer: bool = compiler_disable_sanitizer

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_json(cls, dictionary):
        def decoder(obj) -> CompilerConfig:
            return CompilerConfig(**obj)

        return json.loads(dictionary, object_hook=decoder)

class ProcedureConfig:
    def __init__(
            self,
            build_directory: str,
            output_name: str,
            source_files: List[str],
            additional_libs: Optional[List[str]] = None,
            compile_time_defines: Optional[List[str]] = None,
            compiler_inject_into_args: Optional[List[str]] = None,
            include_paths: Optional[List[str]] = None,
            should_compile: bool = True,
            on_source_change_recompile: bool = False
    ):
        self.build_directory: str = build_directory
        self.output_name: str = output_name
        self.source_files: List[str] = source_files
        self.additional_libs: List[str] = additional_libs or []
        self.compile_time_defines: List[str] = compile_time_defines or []
        self.compiler_inject_into_args: List[str] = compiler_inject_into_args or []
        self.include_paths: List[str] = include_paths or []
        self.should_compile: bool = should_compile
        self.on_source_change_recompile: bool = on_source_change_recompile

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_json(cls, dictionary):
        def decoder(obj) -> ProcedureConfig:
            return ProcedureConfig(**obj)

        return json.loads(dictionary, object_hook=decoder)