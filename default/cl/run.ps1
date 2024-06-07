param(
	[Parameter(Mandatory=$true)]
	[string] $executable_name,

    [Parameter(Mandatory=$false)]
	[string] $compile_time_defines,

    [Parameter(Mandatory=$true)]
	[string] $std_version,

    [Parameter(Mandatory=$true)]
	[bool] $debug_build,

    [Parameter(Mandatory=$true)]
	[bool] $generate_object_files,

    [Parameter(Mandatory=$false)]
	[string] $include_paths,

    [Parameter(Mandatory=$true)]
	[string] $source_paths,

    [Parameter(Mandatory=$false)]
	[string] $lib_paths,
    
    [Parameter(Mandatory=$false)]
	[string] $libs
)

./C-BUILD/default/cl/build.ps1 `
    -executable_name $executable_name `
    -compile_time_define $compile_time_define `
    -std_version $std_version `
    -debug_build $debug_build `
    -generate_object_files $generate_object_files `
    -include_paths $include_paths `
    -source_paths $source_paths `
    -lib_paths $lib_paths `
    -libs $libs

Push-Location ".\examples\cl"
    & "./$executable_name"
Pop-Location