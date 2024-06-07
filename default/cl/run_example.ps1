param(
	[Parameter(Mandatory=$true)]
	[string] $lib_name,

	[Parameter(Mandatory=$true)]
	[string] $executable_name,

    [Parameter(Mandatory=$false)]
	[string] $compile_time_defines,

    [Parameter(Mandatory=$true)]
	[string] $std_version,

    [Parameter(Mandatory=$true)]
	[bool] $debug_build,

	[Parameter(Mandatory=$true)]
	[bool] $build_lib,

    [Parameter(Mandatory=$true)]
	[bool] $generate_object_files,

    [Parameter(Mandatory=$false)]
	[string] $include_paths,

	[Parameter(Mandatory=$true)]
	[string] $source_paths,

	[Parameter(Mandatory=$true)]
	[string] $source_example_paths,

	[Parameter(Mandatory=$false)]
	[string] $additional_libs_for_build,
    
    [Parameter(Mandatory=$false)]
	[string] $additional_libs_for_example
)

./C-BUILD/default/cl/build.ps1 `
	-lib_name $lib_name `
	-executable_name $executable_name `
	-compile_time_defines $compile_time_defines `
	-std_version $std_version `
	-debug_build $debug_build `
	-build_lib $build_lib `
	-include_paths $include_paths `
	-source_paths $source_paths `
	-additional_libs_for_build $additional_libs_for_build `

./C-BUILD/default/cl/build_example.ps1 `
	-executable_name $executable_name `
	-compile_time_defines $compile_time_defines `
	-std_version $std_version `
	-debug_build $debug_build `
	-include_paths $include_paths `
	-source_example_paths $source_example_paths `
	-additional_libs_for_example $additional_libs_for_example


Push-Location ".\examples\cl"
    & "./$executable_name"
Pop-Location