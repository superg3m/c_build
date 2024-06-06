param(
	[Parameter(Mandatory=$true)]
	[string] $executable_name,

    [Parameter(Mandatory=$true)]
	[string] $std_version,

    [Parameter(Mandatory=$true)]
	[bool] $debug,

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

./vars.ps1

if(!(Test-Path -Path ".\examples\cl")) {
    mkdir ".\examples\cl"
}

Push-Location -Path ".\examples\cl"
cl /Fe: $executable_name /Zi "..\*.c" "..\..\build_cl\ckit.lib"
Pop-Location