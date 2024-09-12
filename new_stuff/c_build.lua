local arg = {...}
local COMPILER = arg[2] or "cl"

local Project = loadfile("./project.lua")()
local project = Project:new("CKIT", COMPILER)

-- Do different things depending on the platform
if COMPILER == "cl" then
  project:set_compiler_warning_level("4")
  project:disable_specific_warnings({"5105", "4668", "4820"})
else
  project:set_compiler_warning_level("all")
end

project:set_treat_warnings_as_errors(true)
project:set_debug_with_visual_studio(true)
project:set_rebuild_project_dependencies(true)
-- If project:set_rebuild_project_dependencies is set to (false)
-- then by default it will look at the source files and check if they have been modified since the cache

project:set_project_dependencies({""})
-- -------------------------------------------------------------------------------------
local test_procedure = project:add_procedure("")
test_procedure:set_output_name("test.exe")
test_procedure:set_compile_time_defines({""})
test_procedure:set_include_paths({""})
test_procedure:set_source_files({"../*.c"}, false)
test_procedure:set_additional_libs({""})
-- -------------------------------------------------------------------------------------

project:set_executables_to_run({"test.exe"})
project:build()