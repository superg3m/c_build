import json
import os
import subprocess
import time
from linecache import cache
from typing import Dict

from .Utilities import NORMAL_PRINT, FORMAT_PRINT, DOWN_LEVEL, C_BUILD_EXECUTION_TYPE, UP_LEVEL, GET_LEVEL, GIT_PULL, \
    C_BUILD_IS_DEBUG, IS_WINDOWS, FATAL_PRINT


class Project:
    def __init__(self, MANAGER_COMPILER, project_config: Dict, procedures_config: Dict, is_dependency = False,):
        self.project_name = project_config["project_name"]
        self.project_debug_with_visual_studio = project_config["project_debug_with_visual_studio"]
        self.project_executable_procedures = project_config["project_executable_procedures"]
        self.procedures = [procedure_data for procedure_data in procedures_config.values()]
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
                    GIT_PULL(dependency)
                    cache_dir = os.getcwd()
                    os.chdir(dependency)
                    GIT_PULL("c_build")
                    os.chdir(cache_dir)



                cache_dir = os.getcwd()
                os.chdir(dependency)

                self.__serialize_dependency_data(github_root, dependency)  # only runs if not serialized
                project_data, procedure_data = self.__deserialize_dependency_data()
                project: Project = Project(self.MANAGER_COMPILER, project_data, procedure_data, True)
                project.build()

                os.chdir(cache_dir)

    def build(self):
        execution_type = C_BUILD_EXECUTION_TYPE()
        if execution_type == "RUN":
            self.__run()
            return
        elif execution_type == "DEBUG":
            self.__debug()
            return
        elif execution_type == "CLEAN":
            self.__clean()
            return

        FORMAT_PRINT(f"|----------------------------------------- {self.project_name} -----------------------------------------|")
        UP_LEVEL()
        start_time = time.perf_counter()

        self.build_dependencies(self.project_config)

        for proc_config in self.procedures:
            build_dir = proc_config["build_directory"]
            output_name = proc_config["output_name"]
            if self.__check_procedure_built(build_dir, output_name) and self.is_dependency:
                NORMAL_PRINT(f"Already built procedure: {os.path.join(build_dir, output_name)}, skipping...")
                continue
            self.MANAGER_COMPILER.compile_procedure(proc_config)

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        DOWN_LEVEL()
        FORMAT_PRINT(f"|------------------------------- Time elapsed: {elapsed_time:.2f} seconds -------------------------------|")

    def __run(self):
        print("RUN")

    def __debug(self):
        print("DEBUG")

    def __clean(self):
        print("CLEAN")