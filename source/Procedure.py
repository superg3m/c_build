import time
from source.Utils.InternalUtilities import *

class Procedure:
    def __init__(self, MANAGER_COMPILER, procedure_element: ProcedureConfigElement):
        self.MANAGER_COMPILER = MANAGER_COMPILER
        self.build_directory = procedure_element.build_directory
        self.output_name = procedure_element.output_name
        self.source_files = procedure_element.source_files
        aggregate = []
        for source in self.source_files:
            if source:
                aggregate.extend(RESOLVE_FILE_GLOB(self.build_directory, source, False))
        self.source_files = aggregate
        self.additional_libs = procedure_element.additional_libs
        self.compile_time_defines = procedure_element.compile_time_defines
        self.include_paths = procedure_element.include_paths
        self.compiler_inject_into_args = procedure_element.compiler_inject_into_args

    def compile(self):
        self.MANAGER_COMPILER.compile_procedure(self)

    def clean(self):
        current_dir = os.getcwd()
        current_dir = current_dir.replace("\\", "/")

        current_dir = current_dir + self.build_directory.replace("./", "/")
        if not os.path.exists(self.build_directory):
            return
        FORMAT_PRINT(f"Cleaning: {current_dir}")
        for filename in os.listdir(self.build_directory):
            file_path = os.path.join(self.build_directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    if file_path.endswith(".c") or file_path.endswith(".cpp") or file_path.endswith(".sln"):
                        continue

                    os.unlink(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))


    def debug(self, debug_with_visual_studio):
        debugger = ["raddbg", "devenv"]

        output_splat = self.output_name.split(" ")
        debug_command = [debugger[debug_with_visual_studio], *output_splat]
        cached_current_directory = os.getcwd()
        try:
            os.chdir(self.build_directory)
            debugger_name = debugger[debug_with_visual_studio]
            print(f"{debugger_name} {self.output_name}")
            # Check if the debugger process is already running
            debugger_running = IS_WINDOWS_PROCESS_RUNNING(debugger_name)
            if debugger_running:
                NORMAL_PRINT(f"Debugger already running attaching to process...")
            else:
                NORMAL_PRINT(f"Started new debugger with command: {debug_command}")
                subprocess.Popen(debug_command)

        except FileNotFoundError:
            FATAL_PRINT(f"{debug_command} compiler or executable not found")
            exit(-1)
        finally:
            os.chdir(cached_current_directory)

    def run(self):
        cached_current_directory = os.getcwd()
        try:
            os.chdir(self.build_directory)
            args: list[str] = self.output_name.split(" ")
            executable_name = args.pop(0) # Remove executable name
            executable_path = os.path.join('.', executable_name) if not IS_WINDOWS() else f".\\{executable_name}"
            command = [executable_path] + args
            FORMAT_PRINT(command)
            start_time = time.perf_counter()
            subprocess.run(command, check=True)
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time
            print(f"Process took: {GREEN}{elapsed_time:.2f}{DEFAULT} seconds")
        except FileNotFoundError:
            FATAL_PRINT(f"Executable '{self.output_name}' not found in directory '{self.build_directory}'")
            exit(-1)
        except Exception as e:
            WARN_PRINT(f"Error running executable '{self.output_name}': {e}")
            exit(-1)
        finally:
            os.chdir(cached_current_directory)
