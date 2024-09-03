from new_project import *
from constants import *

COMPILER = "gcc"
project = Project("CKIT", COMPILER)

# Do different things depending on the platform
if COMPILER == "cl":
	project.set_compiler_warning_level("4") # w0 to disable warnings  (not sure if that is accurate but just putting this here)
elif COMPILER in ["gcc", "cc", "clang"]:
	project.set_compiler_warning_level("all") # w0 to disable warnings (not sure if that is accurate but just putting this here)

project.disable_specific_warnings(["5105", "4668", "4820"])
project.set_treat_warnings_as_errors(True)
project.set_debug_with_visual_studio(True)
project.set_rebuild_project_dependencies(True)
# If project.set_rebuild_project_dependencies is set to (False)
# then by default it will look at the source files and check if they have been modified since the cache

# project.set_project_dependencies(["ckg"])
# -------------------------------------------------------------------------------------

test_procedure = project.add_procedure("./CODE/build_" + COMPILER)
test_procedure.set_output_name("test.exe")

test_procedure.set_compile_time_defines([""])
test_procedure.set_include_paths([""])
test_procedure.set_source_files(["../*.c"])
test_procedure.set_additional_libs([""])
project.internal_compiler.compile_procedure(test_procedure)
# -------------------------------------------------------------------------------------

project.set_executables_to_run(["test.exe"])

# vc vars cache
# file cache