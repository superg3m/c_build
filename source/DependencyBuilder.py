import json
import os
import subprocess

from .Project import Project
from .Utilities import INTERNAL_COMPILER, C_BUILD_IS_DEPENDENCY, GET_LEVEL, C_BUILD_IS_DEBUG, \
    C_BUILD_EXECUTION_TYPE, FORMAT_PRINT, GIT_PULL


class DependencyBuilder:
    def __init__(self):
        self.build_type = "debug" if C_BUILD_IS_DEBUG() else "release"
        self.serialized_name = f"c_build_dependency_cache_{INTERNAL_COMPILER.compiler_name}.json"

    def is_serialized(self):
        return os.path.exists(self.serialized_name)

    def __serialize_dependency_data(self, github_root, dependency_name):
        if self.is_serialized():
            return

        if not os.path.exists(dependency_name):
            FORMAT_PRINT(f"missing {dependency_name} cloning...")
            os.system(f"git clone {github_root}/{dependency_name}.git")
        else:
            GIT_PULL(dependency_name)

        os.environ['COMPILER'] = INTERNAL_COMPILER.compiler_name
        os.environ['LEVEL'] = str(GET_LEVEL())
        os.environ['IS_DEPENDENCY'] = str(True) # Make sure it's a string
        env = os.environ.copy()

        original_cached_directory = os.curdir
        os.chdir(dependency_name)
        if os.name == "nt":
            subprocess.call(
                f"python -B -m c_build_script --build_type {self.build_type} --is_dependency {True} --execution_type BUILD",
                shell=True,
                env=env
            )
        else:
            subprocess.call(
                f"python3 -B -m c_build_script --build_type {self.build_type} --is_dependency {True} --execution_type BUILD",
                shell=True,
                env=env
            )
        os.chdir(original_cached_directory)

    def __deserialize_dependency_data(self):
        serialized_file = open(self.serialized_name)
        config = json.load(serialized_file)
        project_config = {}
        procedure_config = {}

        for key, value in config.items():
            if key.startswith("project_"):
                project_config[key] = value
            elif isinstance(value, dict):
                procedure_config[key] = value

        return project_config, procedure_config

    def build_dependencies(self, project_config, github_root = "https://github.com/superg3m"):
        project_name = project_config["project_name"]
        project_dependencies = project_config["project_dependencies"]

        if len(project_dependencies) != 0 and project_dependencies[0] != "":
            FORMAT_PRINT(f"{project_name} depends on:")

        for dependency in project_dependencies:
            self.__serialize_dependency_data(github_root, dependency) # only runs if not serialized
            project_data, procedure_data = self.__deserialize_dependency_data()
            project: Project = Project(project_data, procedure_data, True)
            project.build()