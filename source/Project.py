import asyncio
import json
import os
import subprocess
import time
from linecache import cache
from typing import Dict, List

from .Procedure import Procedure
from .Utilities import NORMAL_PRINT, FORMAT_PRINT, DOWN_LEVEL, C_BUILD_EXECUTION_TYPE, UP_LEVEL, \
    C_BUILD_IS_DEBUG, IS_WINDOWS, FATAL_PRINT, GIT_PULL, CHECK_AND_CONSUME_GIT_PULL

class Project:
    def __init__(self, MANAGER_COMPILER, project_config: Dict, procedures_config: Dict, is_dependency = False,):
        self.project_name = project_config["project_name"]
        self.project_debug_with_visual_studio = project_config.get("project_debug_with_visual_studio", True)
        self.should_rebuild = project_config.get("project_rebuild_project_dependencies", False)
        self.executable_procedures_names = project_config["project_executable_procedures"]
        self.procedures = [Procedure(MANAGER_COMPILER, procedure_data) for procedure_data in procedures_config.values()]
        self.project_executable_procedures = [proc for proc in self.procedures if proc.output_name in self.executable_procedures_names]

        self.is_dependency = is_dependency
        self.project_config = project_config
        self.build_type = "debug" if C_BUILD_IS_DEBUG() else "release"
        self.MANAGER_COMPILER = MANAGER_COMPILER
        self.serialized_name = f"c_build_dependency_cache_{MANAGER_COMPILER.compiler_name}.json"


    def __check_procedure_built(self, build_dir, output_name):
        return os.path.exists(os.path.join(build_dir, output_name))

    def is_serialized(self):
        return os.path.exists(self.serialized_name)

    def __serialize_dependency_data(self, github_root, dependency_name):
        if self.is_serialized():
            return

        if IS_WINDOWS():
            subprocess.call(
                f"python -B -m c_build_script --is_dependency true --compiler_name {self.MANAGER_COMPILER.compiler_name}",
                shell=True
            )
        else:
            subprocess.call(
                f"python3 -B -m c_build_script --is_dependency true --compiler_name {self.MANAGER_COMPILER.compiler_name}",
                shell=True
            )

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
            if dependency:
                if not os.path.exists(dependency):
                    FORMAT_PRINT(f"missing {dependency} cloning...")
                    os.system(f"git clone {github_root}/{dependency}.git")
                    cache_dir = os.getcwd()
                    os.chdir(dependency)
                    os.system(f"git clone https://github.com/superg3m/c_build.git")
                    os.chdir(cache_dir)
                else:
                    GIT_PULL(dependency, self.procedures)
                    GIT_PULL(f"{dependency}/c_build", [])

                cache_dir = os.getcwd()
                os.chdir(dependency)

                self.__serialize_dependency_data(github_root, dependency)  # only runs if not serialized
                project_data, procedure_data = self.__deserialize_dependency_data()
                project: Project = Project(self.MANAGER_COMPILER, project_data, procedure_data, True)
                project.should_rebuild = self.should_rebuild
                project.build()

                os.chdir(cache_dir)

    def build(self, override = False):
        execution_type = C_BUILD_EXECUTION_TYPE()
        if execution_type == "RUN" and not override:
            self.__run()
            return
        elif execution_type == "DEBUG" and not override:
            self.__debug()
            return
        elif execution_type == "CLEAN" and not override:
            self.__clean()
            return

        FORMAT_PRINT(f"|----------------------------------------- {self.project_name} -----------------------------------------|")
        UP_LEVEL()
        start_time = time.perf_counter()

        self.build_dependencies(self.project_config)

        for proc in self.procedures:
            if (self.__check_procedure_built(proc.build_directory, proc.output_name) and
                self.is_dependency and not self.should_rebuild and not CHECK_AND_CONSUME_GIT_PULL()):
                NORMAL_PRINT(f"Already built procedure: {os.path.join(proc.build_directory, proc.output_name)}, skipping...")
                continue
            proc.compile()

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        DOWN_LEVEL()
        FORMAT_PRINT(f"|------------------------------- Time elapsed: {elapsed_time:.2f} seconds -------------------------------|")

    def __run(self):
        expected_names = [proc.output_name for proc in self.procedures if proc.output_name.endswith(".exe")]
        project_executable_names = [proc.output_name for proc in self.project_executable_procedures]
        intersection = set(project_executable_names) & set(expected_names)

        if len(intersection) == 0:
            FATAL_PRINT("No available executable procedures!")
            FATAL_PRINT(f"Got: {self.executable_procedures_names} | Expected: {expected_names}")
            exit(-1)

        for proc in self.project_executable_procedures:
            if not self.__check_procedure_built(proc.build_directory, proc.output_name):
                proc.compile()
            proc.run()

    def __debug(self):
        self.project_executable_procedures[0].debug(self.project_debug_with_visual_studio)

    def __clean(self):
        for proc in self.procedures:
            proc.clean()