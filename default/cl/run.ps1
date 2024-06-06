param(
	[Parameter(Mandatory=$true)]
	[string] $executable_name,

    [Parameter(Mandatory=$true)]
	[string] $compile_time_defines,

    [Parameter(Mandatory=$true)]
	[string] $std_version,

    [Parameter(Mandatory=$true)]
	[bool] $debug_build,

    [Parameter(Mandatory=$true)]
	[bool] $generate_object_files,

    [Parameter(Mandatory=$true)]
	[string] $include_paths,

    [Parameter(Mandatory=$true)]
	[string] $source_paths,

    [Parameter(Mandatory=$true)]
	[string] $lib_paths,
    
    [Parameter(Mandatory=$true)]
	[string] $libs
)

