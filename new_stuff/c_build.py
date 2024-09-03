from new_project import *
from constants import *

COMPILER = "cl"

project = Project("CKIT", COMPILER)

# Do different things depending on the platform
if PLATFORM_WINDOW():
	project.set_compiler_warning_level("4") # w0 to disable warnings  (not sure if that is accurate but just putting this here)
elif PLATFORM_LINUX():
	project.set_compiler_warning_level("wall") # w0 to disable warnings (not sure if that is accurate but just putting this here)

project.disable_specific_warnings(["5105", "4668", "4820"])
project.set_treat_warnings_as_errors(True)
project.set_debug_with_visual_studio(True)
project.set_rebuild_project_dependencies(True)
# If project.set_rebuild_project_dependencies is set to (False)
# then by default it will look at the source files and check if they have been modified since the cache

project.set_project_dependencies(["ckg"])

# Do different things depending on the platform
if PLATFORM_WINDOW():
	project.inject_as_argument("some other thing here") # w0 to disable warnings  (not sure if that is accurate but just putting this here)
elif PLATFORM_LINUX():
	project.inject_as_argument("/MP") # w0 to disable warnings (not sure if that is accurate but just putting this here)
# -------------------------------------------------------------------------------------

lib_procedure = project.add_procedure("./ckit_build_" + COMPILER)
lib_procedure.set_output_name("ckit.lib")

lib_procedure.set_compile_time_defines([""])
lib_procedure.set_include_paths([""])
lib_procedure.set_source_files(["../ckg/ckg.c", "../ckit.c"])
lib_procedure.set_additional_libs([""])

# -------------------------------------------------------------------------------------

test_exe_procedure = project.add_procedure("./Tests/CoreTest/build_" + COMPILER)
test_exe_procedure.set_output_name("test_ckit.exe")

test_exe_procedure.set_compile_time_defines([""])
test_exe_procedure.set_include_paths([""])
test_exe_procedure.set_source_files(["../*.c"], True)
test_exe_procedure.set_additional_libs([f"../../../ckit_build_{COMPILER}/ckit.lib"])

# -------------------------------------------------------------------------------------

graphics_exe_procedure = project.add_procedure("./Tests/GraphicsTest/build_" + COMPILER)
graphics_exe_procedure.set_output_name("test_graphics_ckit.exe")

graphics_exe_procedure.set_compile_time_defines([""])
graphics_exe_procedure.set_include_paths([""])
graphics_exe_procedure.set_source_files(["../*.c"])
graphics_exe_procedure.set_additional_libs([f"../../../ckit_build_{COMPILER}/ckit.lib"])

# -------------------------------------------------------------------------------------

project.set_executables_to_run(["test_graphics_ckit.exe"])

# vc vars cache
# file cache