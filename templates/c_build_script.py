import argparse
from c_build.new_stuff.new_project import *

parser = argparse.ArgumentParser(description='c_build_script')
parser.add_argument('--compiler', type=str, help='Compiler to use (e.g. gcc, clang)')
parser.add_argument('--build_type', type=str, help='Build type (e.g. debug, release)')
args = parser.parse_args()

COMPILER = args.compiler or "cl"
project = Project("CKIT", COMPILER)

# Do different things depending on the platform
if COMPILER == "cl":
	project.set_compiler_warning_level("4")
	project.disable_specific_warnings(["5105", "4668", "4820"])
elif COMPILER in ["gcc", "cc", "clang"]:
	project.set_compiler_warning_level("all")

project.set_treat_warnings_as_errors(True)
project.set_debug_with_visual_studio(True)
project.set_rebuild_project_dependencies(True)
# If project.set_rebuild_project_dependencies is set to (False)
# then by default it will look at the source files and check if they have been modified since the cache

project.set_project_dependencies([""])
# -------------------------------------------------------------------------------------

test_procedure = project.add_procedure(f"build_{COMPILER}")
test_procedure.set_output_name("test.exe")

test_procedure.set_compile_time_defines([""])
test_procedure.set_include_paths([""])
test_procedure.set_source_files(["../new_stuff/CODE/*.c"], False)
test_procedure.set_additional_libs([""])
# -------------------------------------------------------------------------------------

project.set_executables_to_run(["test.exe"])
project.build(args.build_type)