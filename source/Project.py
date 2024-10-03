import os
import time
from typing import Dict

from .DependencyBuilder import DependencyBuilder
from .Utilities import NORMAL_PRINT, FORMAT_PRINT, DOWN_LEVEL, C_BUILD_EXECUTION_TYPE, UP_LEVEL

class Project:
    def __init__(self, project_config: Dict, procedures_config: Dict, is_dependency = False,):
        self.project_name = project_config["project_name"]
        self.project_debug_with_visual_studio = project_config["project_debug_with_visual_studio"]
        self.project_executable_procedures = project_config["project_executable_procedures"]
        self.procedures = [procedure_data for procedure_data in procedures_config.values()]
        self.is_dependency = is_dependency
        self.project_config = project_config

    def __check_procedure_built(self, build_dir, output_name):
        return os.path.exists(os.path.join(build_dir, output_name))

    def build(self, MANAGER_COMPILER):
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

        builder: DependencyBuilder = DependencyBuilder(MANAGER_COMPILER)
        builder.build_dependencies(self.project_config)

        for proc_config in self.procedures:
            build_dir = proc_config["build_directory"]
            output_name = proc_config["output_name"]
            if self.__check_procedure_built(build_dir, output_name) and self.is_dependency:
                NORMAL_PRINT(f"Already built procedure: {os.path.join(build_dir, output_name)}, skipping...")
                continue
            MANAGER_COMPILER.compile_procedure(proc_config)

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