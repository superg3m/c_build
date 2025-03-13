import copy
import time
from .Procedure import Procedure
from .Utilities import *

class Project:
    def __init__(self, MANAGER_COMPILER, project_config: ProjectConfig, procedures_config: dict[str, ProcedureConfigElement], is_dependency = False,):
        self.project_name = project_config.project_name
        self.project_debug_with_visual_studio: bool = project_config.project_debug_with_visual_studio
        self.executable_procedures_names = project_config.project_executable_procedures
        self.procedures = [Procedure(MANAGER_COMPILER, procedure_data) for procedure_data in procedures_config.values()]
        self.project_executable_procedures = []
        for proc in self.procedures:
            for name in self.executable_procedures_names:
                if proc.output_name in name:
                    self.project_executable_procedures.append(proc)

        self.is_dependency = is_dependency

        if not self.is_dependency:
            self.project_rebuild_project_dependencies: bool = project_config.project_rebuild_project_dependencies
            self.build_type = "debug" if C_BUILD_IS_DEBUG() else "release"

        self.project_config = project_config
        self.MANAGER_COMPILER = MANAGER_COMPILER
        self.serialized_name = f"c_build_dependency_cache_{MANAGER_COMPILER.cc.compiler_name}.json"

    def __check_procedure_built(self, build_dir, output_name):
        return os.path.exists(os.path.join(build_dir, output_name))

    def is_serialized(self):
        return os.path.exists(self.serialized_name)

    def __serialize_dependency_data(self):
        if IS_WINDOWS():
            subprocess.call(
                f"python -B -m c_build_script --is_dependency true --compiler_name {self.MANAGER_COMPILER.cc.compiler_name}",
                shell=True
            )
        else:
            subprocess.call(
                f"python3 -B -m c_build_script --is_dependency true --compiler_name {self.MANAGER_COMPILER.cc.compiler_name}",
                shell=True
            )

    def __deserialize_dependency_data(self) -> (ProjectConfig, dict[str, ProcedureConfigElement]):
        serialized_file = open(self.serialized_name)

        config = json.load(serialized_file)
        project_config = {}
        procedure_config = {}

        for key, value in config.items():
            if key.startswith("project_"):
                project_config[key] = value
            elif isinstance(value, dict):
                procedure_config[key] = ProcedureConfigElement(**value)

        return ProjectConfig(**project_config), procedure_config

    def build_dependencies(self, project_config: ProjectConfig, github_root = "https://github.com/superg3m"):
        project_name = project_config.project_name
        project_dependencies = project_config.project_dependencies

        if len(project_dependencies) != 0 and project_dependencies[0] != "":
            FORMAT_PRINT(f"{project_name} depends on:")

        for dependency in project_dependencies: # This exists early if there are no dependencies
            if dependency:
                if not os.path.exists(dependency):
                    FORMAT_PRINT(f"missing {dependency} cloning...")
                    os.system(f"git clone {github_root}/{dependency}.git")
                    cache_dir = os.getcwd()
                    os.chdir(dependency)
                    os.system(f"git clone https://github.com/superg3m/c_build.git")
                    os.chdir(cache_dir)
                else:
                    GIT_PULL(dependency) # This will be optional!

                cache_dir = os.getcwd()
                os.chdir(dependency)

                if not self.is_serialized():
                    self.__serialize_dependency_data()

                project_config, procedure_config = self.__deserialize_dependency_data()
                project: Project = Project(self.MANAGER_COMPILER, project_config, procedure_config, True)
                project.project_rebuild_project_dependencies = self.project_rebuild_project_dependencies
                project.build_type = self.build_type
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
            if not self.project_rebuild_project_dependencies:
                if (self.__check_procedure_built(proc.build_directory, proc.output_name) and
                    self.is_dependency and PEEK_GIT_PULL() == False):
                    NORMAL_PRINT(f"Already built procedure: {os.path.join(proc.build_directory, proc.output_name)}, skipping...")
                    continue

            proc.compile()

        CONSUME_GIT_PULL()

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        DOWN_LEVEL()
        FORMAT_PRINT(f"|------------------------------- Time elapsed: {elapsed_time:.2f} seconds -------------------------------|")

    def __run(self):
        if len(self.project_executable_procedures) == 0:
            FATAL_PRINT("No available executable procedures!")
            FATAL_PRINT(
                f"Got: {self.executable_procedures_names} | Expected: {[proc.output_name for proc in self.procedures]}")
            sys.exit(1)

        initial_range = len(self.executable_procedures_names)
        for i in range(initial_range):
            executable_name_with_args = self.executable_procedures_names.pop(0)
            proc = next((proc for proc in self.project_executable_procedures if proc.output_name in executable_name_with_args), None)
            if not self.__check_procedure_built(proc.build_directory, proc.output_name):
                proc.compile()

            deep_copy_proc = copy.deepcopy(proc)
            deep_copy_proc.output_name = executable_name_with_args
            deep_copy_proc.run()


    def __debug(self):
        self.project_executable_procedures[0].output_name = self.executable_procedures_names[0]
        self.project_executable_procedures[0].debug(self.project_debug_with_visual_studio)

    def __clean(self):
        for proc in self.procedures:
            proc.clean()