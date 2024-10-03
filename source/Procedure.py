import os
import subprocess
from typing import Dict

from .Utilities import IS_WINDOWS, FATAL_PRINT

class Procedure:
    def __init__(self, MANAGER_COMPILER, procedure_config: Dict):
        self.MANAGER_COMPILER = MANAGER_COMPILER
        self.build_directory = procedure_config["build_directory"]
        self.output_name = procedure_config["output_name"]
        self.source_files = procedure_config["source_files"]
        self.additional_libs = procedure_config["additional_libs"]
        self.compile_time_defines = procedure_config["compile_time_defines"]
        self.include_paths = procedure_config["include_paths"]

    def compile(self):
        self.MANAGER_COMPILER.compile_procedure(self)

    def clean(self):
        print("sdfsdf")


    def debug(self):
        print("sdfsdf")

    def run(self):
        cached_current_directory = os.getcwd()
        try:
            os.chdir(self.build_directory)
            executable_path = f"./{self.output_name}" if not IS_WINDOWS() else f".\\{self.output_name}"
            subprocess.run([executable_path])
        except FileNotFoundError:
            FATAL_PRINT(f"Executable '{self.output_name}' not found in directory '{self.build_directory}'")
            exit(-1)
        except Exception as e:
            FATAL_PRINT(f"Error running executable '{self.output_name}': {e}")
            exit(-1)
        finally:
            os.chdir(cached_current_directory)