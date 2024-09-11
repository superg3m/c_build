-- Import the project module
local project = require("project")

-- Define an enum for the command line arguments
local Arg = {
    COMPILER_ARG = 2
}

-- Get the compiler from the command line arguments
local COMPILER = arg[Arg.COMPILER_ARG] or "cl"

-- Create a new project
local project = project.new("CKIT", COMPILER)

-- Do different things depending on the platform
if COMPILER == "cl" then
    project:set_compiler_warning_level("4")
    project:disable_specific_warnings({"5105", "4668", "4820"})
elseif COMPILER == "gcc" or COMPILER == "cc" or COMPILER == "clang" then
    project:set_compiler_warning_level("all")
end

-- Set project options
project:set_treat_warnings_as_errors(true)
project:set_debug_with_visual_studio(true)
project:set_rebuild_project_dependencies(true)

-- Set project dependencies
project:set_project_dependencies({""})

-- Create a new procedure
local test_procedure = project:add_procedure("")
test_procedure:set_output_name("test.exe")

-- Set procedure options
test_procedure:set_compile_time_defines({""})
test_procedure:set_include_paths({""})
test_procedure:set_source_files({"../*.c"}, false)
test_procedure:set_additional_libs({""})

-- Set executables to run
project:set_executables_to_run({"test.exe"})

-- Build the project
project:build()