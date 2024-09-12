# Get the compiler from the command line argument or default to "cl"
$compiler = $args[1] ?? "cl"

# Load the project configuration from project.lua
$project = & ./project.lua

# Create a new project instance
$project = $project::new("CKIT", $compiler)

# Configure the project based on the compiler
switch ($compiler) {
    "cl" {
        $project::set_compiler_warning_level("4")
        $project::disable_specific_warnings(@("5105", "4668", "4820"))
    }
    { $_ -in @("gcc", "cc", "clang") } {
        $project::set_compiler_warning_level("all")
    }
}

# Set common project settings
$project::set_treat_warnings_as_errors($true)
$project::set_debug_with_visual_studio($true)
$project::set_rebuild_project_dependencies($true)

# Set project dependencies
$project::set_project_dependencies(@(""))

# Create a test procedure
$testProcedure = $project::add_procedure("")
$testProcedure::set_output_name("test.exe")

# Configure the test procedure
$testProcedure::set_compile_time_defines(@(""))
$testProcedure::set_include_paths(@(""))
$testProcedure::set_source_files(@("../*.c"), $false)
$testProcedure::set_additional_libs(@(""))

# Set executables to run
$project::set_executables_to_run(@("test.exe"))

# Build the project
$project::build()