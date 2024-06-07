param(
	[Parameter(Mandatory=$true)]
	[string] $executable_name,

    [Parameter(Mandatory=$true)]
    [bool]$debug_with_visual_studio,

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

    [Parameter(Mandatory=$true)]
	[string] $source_example_paths,
    
    [Parameter(Mandatory=$false)]
	[string] $additional_libs_for_example
)

if (!(Test-Path -Path $executable_name)) {
    Write-Host "ERROR: Can't find exe, building..." -ForegroundColor Red

    ./C-BUILD/default/cl/build.ps1 `
        -executable_name $executable_name `
        -std_version $std_version `
        -debug_build $debug_build `
        -generate_object_files $generate_object_files `
        -include_paths $include_paths `
        -source_paths $source_paths `
        -additional_libs_for_example $additional_libs_for_example
    Push-Location "./build_cl"
    if ($debug_with_visual_studio -eq $true) {
        ./vars.ps1
        devenv $executable_name
    } else {
        #& "raddbg" $executable_name
    }
    Pop-Location
} else {
    Push-Location "./build_cl"
    if ($debug_with_visual_studio -eq $true) {
        ./vars.ps1
        devenv $executable_name
    } else {
        #& "raddbg" $executable_name
    }
    Pop-Location
}