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

Write-Host $PWD

Push-Location "./C-BUILD/default/cl"
if (!(Test-Path -Path $executable_name)) {
    Write-Host "ERROR: Can't find exe, building..." -ForegroundColor Red

    ./build_example.ps1 `
        -executable_name $executable_name `
        -std_version $std_version `
        -debug_build $debug_build `
        -generate_object_files $generate_object_files `
        -include_paths $include_paths `
        -source_paths $source_paths `
        -lib_paths $lib_paths `
        -libs $libs
    
    if ($debug_with_visual_studio -eq $true) {
        devenv $executable_name
    } else {
        & "raddbg" $executable_name
    }
} else {
    ./vars.ps1
    if ($debug_with_visual_studio -eq $true) {
        devenv $executable_name
    } else {
        & "raddbg" $executable_name
    }
}
Pop-Location