import copy
import time
from doctest import debug

from .Procedure import Procedure
from .Utils.FileWatcher import FileWatcher
from .Utils.InternalUtilities import *


class Project(ProjectConfig):
    def __init__(self, MANAGER_COMPILER, pc: ProjectConfig, procedures: dict[str, ProcedureConfig], is_dependency=False):
        super().__init__(**pc.to_dict())
        self.MANAGER_COMPILER = MANAGER_COMPILER
        self.pc = pc
        self.is_dependency = is_dependency
        self.procedures = [Procedure(MANAGER_COMPILER, procedure_data) for procedure_data in procedures.values()]
        self.executable_procedures = []

        for name in self.project_executable_names:
            for proc in self.procedures:
                if proc.output_name in name:
                    self.executable_procedures.append(proc)


        self.build_type = C_BUILD_BUILD_TYPE()
        self.serialized_name = f"c_build_dependency_cache_{self.MANAGER_COMPILER.compiler_name}_{self.build_type}.json"

    @classmethod
    def __check_procedure_built(cls, build_dir, output_name):
        return os.path.exists(os.path.join(build_dir, output_name))

    def __serialize_dependency_data(self):
        if IS_WINDOWS():
            subprocess.call(
                f"python -B -m c_build_script --is_dependency true --build_type {self.build_type} --compiler_name {self.MANAGER_COMPILER.compiler_name}",
                shell=True
            )
        else:
            subprocess.call(
                f"python3 -B -m c_build_script --is_dependency true --build_type {self.build_type} --compiler_name {self.MANAGER_COMPILER.compiler_name}",
                shell=True
            )

    def __deserialize_dependency_data(self) -> (ProjectConfig, dict[str, ProcedureConfig]):
        serialized_name = f"c_build_dependency_cache_{self.MANAGER_COMPILER.compiler_name}_{self.build_type}.json"
        serialized_file = open(serialized_name)

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
    def build_dependencies(self, project_config: ProjectConfig):
        project_name = project_config.project_name
        project_dependencies = project_config.project_dependencies

        if len(project_dependencies) != 0 and project_dependencies[0] != "":
            FORMAT_PRINT(f"{project_name} depends on:")

        for dependency in project_dependencies:  # This exits early if there are no dependencies
            if not dependency.name:
                continue

            cache_dir = os.getcwd()

            if not os.path.exists(dependency.name):
                FORMAT_PRINT(f"missing {dependency.name} cloning...")
                result = subprocess.run(
                    ["git", "clone", "-b ", f"{dependency.branch_name}", f"{dependency.host}/{dependency.name}"],
                    capture_output=True, text=True)
                if result.returncode != 0:
                    WARN_PRINT("Fail to clone")
                    WARN_PRINT("Retrying clone with main branch")
                    os.system(f"git clone -b main {dependency.host}/{dependency.name}")
            else:
                os.chdir(dependency.name)
                current_branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True).stdout.strip()
                print(current_branch)
                print(dependency.branch_name)
                print(dependency.branch_name != current_branch)
                if dependency.branch_name != current_branch:
                    result = subprocess.run(["git", "checkout", dependency.branch_name])
                    if result.returncode != 0:
                        FATAL_PRINT(f"Failed to checkout '{dependency.branch_name}' branch from {dependency.name}")
                        WARN_PRINT(
                            f"Available Branches:\n{subprocess.run(["git", "branch", "-r"], capture_output=True, text=True).stdout}")
                        os.chdir(cache_dir)
                        exit(-1)

                os.chdir(cache_dir)

            os.chdir(dependency.name)

            if not os.path.exists(self.serialized_name):
                self.__serialize_dependency_data()

            project_config, procedure_config = self.__deserialize_dependency_data()
            project: Project = Project(self.MANAGER_COMPILER, project_config, procedure_config, True)
            project.project_rebuild_project_dependencies = self.project_rebuild_project_dependencies
            project.build_type = self.build_type
            project.build()

            os.chdir(cache_dir)


    # Make this more apparent when you do this?
    def invalidate_dependency_cache(self):
        for dependency in self.project_dependencies:
            if not dependency.name or not os.path.exists(dependency.name):
                continue

            if dependency.always_pull and GIT_PULL(dependency.name):
                json_to_remove = f"./{dependency.name}/{self.serialized_name}"
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
            sanitizer_enabled_and_debug = not self.MANAGER_COMPILER.compiler_disable_sanitizer and self.build_type == "debug"
            if self.project_rebuild_project_dependencies or sanitizer_enabled_and_debug:
                proc.compile()
                continue

            already_built = self.__check_procedure_built(proc.build_directory, proc.output_name)
            no_git_changes = not PEEK_GIT_PULL()
            if already_built and self.is_dependency and no_git_changes:
                proc_name = os.path.join(proc.build_directory, proc.output_name)
                NORMAL_PRINT(f"Already built procedure: {proc_name}, skipping...")
            else:
                proc.compile()

        CONSUME_GIT_PULL()

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        DOWN_LEVEL()
        FORMAT_PRINT(
            f"|------------------------------- Time elapsed: {elapsed_time:.2f} seconds -------------------------------|")

    def __run(self):
        if len(self.project_executable_names) == 0:
            FATAL_PRINT("No available executable procedures!")
            FATAL_PRINT(
                f"Got: {self.project_executable_names} | Expected: {[proc.output_name for proc in self.procedures]}")
            sys.exit(1)

        initial_range = len(self.project_executable_names)

        def on_file_change(original_directory, proc: Procedure, file_name: str):
            print(f"File changed: {file_name}")
            print(f"Procedure: {proc.output_name}")
            cached_current_directory = os.getcwd()
            try:
                os.chdir(original_directory)
                proc.compile()
            finally:
                os.chdir(cached_current_directory)

        watcher = FileWatcher(os.getcwd(), self.procedures, on_file_change)
        watcher.start()
        for i in range(initial_range):
            executable_name_with_args = self.project_executable_names.pop(0)
            proc = self.executable_procedures[i]
            if not self.__check_procedure_built(proc.build_directory, proc.output_name):
                proc.compile()

            proc.output_name = executable_name_with_args
            proc.run()

        watcher.stop()

    def __debug(self):
        self.executable_procedures[0].output_name = self.project_executable_names[0]
        self.executable_procedures[0].debug(self.project_debug_with_visual_studio)

    def __clean(self):
        for proc in self.procedures:
            proc.clean()