import time
from .Procedure import Procedure
from .Utils.FileWatcher import FileWatcher
from .Utils.InternalUtilities import *


class Project(ProjectConfig):
    def __init__(self, MANAGER_COMPILER, pc: ProjectConfig, procedures: dict[str, ProcedureConfig], is_dependency=False):
        super().__init__(**pc.to_dict())
        self.MANAGER_COMPILER = MANAGER_COMPILER
        self.pc = pc
        self.serialized_name = f"c_build_dependency_cache_{MANAGER_COMPILER.compiler_name}.json"
        self.is_dependency = is_dependency
        self.procedures = [Procedure(MANAGER_COMPILER, procedure_data) for procedure_data in procedures.values()]
        self.project_executable_procedures = []
        for name in self.executable_procedures_names:
            for proc in self.procedures:
                if proc.output_name in name:
                    self.project_executable_procedures.append(proc)

        if not self.is_dependency:
            self.build_type = "debug" if C_BUILD_IS_DEBUG() else "release"

    @classmethod
    def __check_procedure_built(cls, build_dir, output_name):
        return os.path.exists(os.path.join(build_dir, output_name))

    def is_serialized(self):
        return os.path.exists(self.serialized_name)

    def __serialize_dependency_data(self):
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

    def __deserialize_dependency_data(self) -> (ProjectConfig, dict[str, ProcedureConfig]):
        serialized_file = open(self.serialized_name)

        config = json.load(serialized_file)
        project_config = {}
        procedure_config = {}

        for key, value in config.items():
            if key.startswith("project_"):
                project_config[key] = value
            elif isinstance(value, dict):
                procedure_config[key] = ProcedureConfig(**value)

        return ProjectConfig(**project_config), procedure_config

    # Clean this up
    def build_dependencies(self, project_config: ProjectConfig, github_root="https://github.com/superg3m"):
        project_name = project_config.project_name
        project_dependencies = project_config.project_dependencies

        if len(project_dependencies) != 0 and project_dependencies[0] != "":
            FORMAT_PRINT(f"{project_name} depends on:")

        for dependency in project_dependencies:  # This exits early if there are no dependencies
            if dependency:
                if not os.path.exists(dependency):
                    FORMAT_PRINT(f"missing {dependency} cloning...")
                    os.system(f"git clone {github_root}/{dependency}.git")

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

    # Make this more apparent when you do this?
    def invalidate_dependency_cache(self):
        for dependency_name in self.project_dependencies:
            if dependency_name and os.path.exists(dependency_name) and GIT_PULL(dependency_name):
                for compiler_name in VALID_COMPILERS:
                    serialized_name = f"c_build_dependency_cache_{compiler_name}.json"
                    json_to_remove = f"./{dependency_name}/{serialized_name}"
                    if os.path.exists(json_to_remove):
                        os.remove(json_to_remove)

    def build(self):
        execution_type = C_BUILD_EXECUTION_TYPE()
        if execution_type == "BUILD":
            self.invalidate_dependency_cache()
            self.__build()
            return
        if execution_type == "RUN":
            self.__run()
            return
        elif execution_type == "DEBUG":
            self.__debug()
            return
        elif execution_type == "CLEAN":
            self.__clean()
            return


    def __build(self):
        FORMAT_PRINT(
            f"|----------------------------------------- {self.project_name} -----------------------------------------|")
        UP_LEVEL()
        start_time = time.perf_counter()

        self.build_dependencies(self.pc)

        for proc in self.procedures:
            if not self.project_rebuild_project_dependencies:
                if (self.__check_procedure_built(proc.build_directory, proc.output_name) and
                        self.is_dependency and PEEK_GIT_PULL() == False):
                    NORMAL_PRINT(
                        f"Already built procedure: {os.path.join(proc.build_directory, proc.output_name)}, skipping...")
                    continue

            proc.compile()

        CONSUME_GIT_PULL()

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        DOWN_LEVEL()
        FORMAT_PRINT(
            f"|------------------------------- Time elapsed: {elapsed_time:.2f} seconds -------------------------------|")

    def __run(self):
        if len(self.project_executable_procedures) == 0:
            FATAL_PRINT("No available executable procedures!")
            FATAL_PRINT(
                f"Got: {self.executable_procedures_names} | Expected: {[proc.output_name for proc in self.procedures]}")
            sys.exit(1)

        initial_range = len(self.project_executable_procedures)
        for i in range(initial_range):
            executable_name_with_args = self.executable_procedures_names.pop(0)
            proc = self.project_executable_procedures[i]
            if not self.__check_procedure_built(proc.build_directory, proc.output_name):
                proc.compile()

            proc.output_name = executable_name_with_args

            def on_file_change(proc: Procedure, file_name: str):
                print(f"File changed: {file_name}")
                proc.compile()

            watcher = FileWatcher(proc.source_files, on_file_change)
            watcher.start()
            proc.run()
            watcher.stop()

    def __debug(self):
        self.project_executable_procedures[0].output_name = self.executable_procedures_names[0]
        self.project_executable_procedures[0].debug(self.project_debug_with_visual_studio)

    def __clean(self):
        for proc in self.procedures:
            proc.clean()