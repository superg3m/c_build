import json

class ProjectConfig:
    def __init__(self, project_name: str, project_dependencies: list[str], project_debug_with_visual_studio: bool, project_rebuild_project_dependencies: bool, project_executable_procedures: list[str]):
        self.project_name: str = project_name
        self.project_dependencies: list[str] = project_dependencies
        self.project_debug_with_visual_studio: bool = project_debug_with_visual_studio
        self.project_rebuild_project_dependencies: bool = project_rebuild_project_dependencies
        self.project_executable_procedures: list[str] = project_executable_procedures

    def __repr__(self):
        return json.dumps(self.__dict__, indent=4)

    def to_dict(self):
        return self.__dict__


class CompilerConfig:
    def __init__(self, compiler_name: str, compiler_std_version: str, compiler_warning_level: str, compiler_disable_specific_warnings: list[str], compiler_treat_warnings_as_errors: bool, compiler_disable_warnings: bool, compiler_disable_sanitizer: bool):
        self.compiler_name: str = compiler_name
        self.compiler_std_version: str = compiler_std_version
        self.compiler_warning_level: str = compiler_warning_level
        self.compiler_disable_specific_warnings: list[str] = compiler_disable_specific_warnings
        self.compiler_treat_warnings_as_errors: bool = compiler_treat_warnings_as_errors
        self.compiler_disable_warnings: bool = compiler_disable_warnings
        self.compiler_disable_sanitizer: bool = compiler_disable_sanitizer

    def __repr__(self):
        return json.dumps(self.__dict__, indent=4)

    def to_dict(self):
        return self.__dict__


class ProcedureConfigElement:
    def __init__(self, build_directory: str, output_name: str, source_files: list[str], additional_libs: list[str], compile_time_defines: list[str], compiler_inject_into_args: list[str], include_paths: list[str]):
        self.build_directory: str = build_directory
        self.output_name: str = output_name
        self.source_files: list[str] = source_files
        self.additional_libs: list[str] = additional_libs
        self.compile_time_defines: list[str] = compile_time_defines
        self.compiler_inject_into_args: list[str] = compiler_inject_into_args
        self.include_paths: list[str] = include_paths

    def __repr__(self):
        return json.dumps(self.__dict__, indent=4)

    def to_dict(self):
        return self.__dict__