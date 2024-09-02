
# Experimental

project = project_create("CKIT")
project.set_di
project.set_github_root(project, "https://github.com/superg3m")
project.set_compiler(project, "cl")
project.set_std_version(project, "c11")

# Do different things depending on the platform
if (platfrom.WINDOW) then
	project.set_compiler_warning_level(project, "w4") # w0 to disable warnings  (not sure if that is accurate but just putting this here)
elseif (platfrom.LINUX) then
	project.set_compiler_warning_level(project, "wall") # w0 to disable warnings (not sure if that is accurate but just putting this here)
end()

project.disable_specific_warnings(project, ["5105", "4668", "4820"])
project.set_treat_warnings_as_errors(True)
project.set_debug_with_visual_studio(True)
project.set_rebuild_project_dependencies(True)
# If project.set_rebuild_project_dependencies is set to (False)
# then by default it will look at the source files and check if they have been modified since the cache


project.set_project_dependencies(project, ["ckg"])

# Do different things depending on the platform
if (platfrom.WINDOW):
	project.inject_as_argument(project, "some other thing here") # w0 to disable warnings  (not sure if that is accurate but just putting this here)
elif (platfrom.LINUX):
	project.inject_as_argument(project, "/MP") # w0 to disable warnings (not sure if that is accurate but just putting this here)
# -------------------------------------------------------------------------------------

lib_procedure = procedure_create("./ckit_build_" + project.compiler_type)
lib_procedure.set_output_name(lib_procedure, "ckit.lib")

lib_procedure.set_compile_time_defines(lib_procedure, [""])
lib_procedure.set_include_paths(lib_procedure, [""])
lib_procedure.set_source_files(lib_procedure, ["../ckg/ckg.c", "../ckit.c"])
lib_procedure.set_additional_libs(lib_procedure, [""])

# -------------------------------------------------------------------------------------

test_exe_procedure = procedure_create("./Tests/CoreTest/build_" + project.compiler_type)
test_exe_procedure.set_output_name("test_ckit.exe")

test_exe_procedure.set_compile_time_defines(test_exe_procedure, [""])
test_exe_procedure.set_include_paths(test_exe_procedure, [""])
test_exe_procedure.set_source_files(test_exe_procedure, ["../*.c"])
test_exe_procedure.set_additional_libs(test_exe_procedure, ["../../../ckit_build_$compiler_type/ckit.lib"])

# -------------------------------------------------------------------------------------

graphics_exe_procedure = procedure_create("./Tests/GraphicsTest/build_" + project.compiler_type)
graphics_exe_procedure.set_output_name("test_graphics_ckit.exe")

graphics_exe_procedure.set_compile_time_defines(graphics_exe_procedure, [""])
graphics_exe_procedure.set_include_paths(graphics_exe_procedure, [""])
graphics_exe_procedure.set_source_files(graphics_exe_procedure, ["../*.c"])
graphics_exe_procedure.set_additional_libs(graphics_exe_procedure, ["../../../ckit_build_$compiler_type/ckit.lib"])

# -------------------------------------------------------------------------------------

project.set_executables_to_run(["test_graphics_ckit.exe"])

# vc vars cache
# file cache