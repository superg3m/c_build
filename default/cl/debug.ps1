param(
    [Parameter(Mandatory=$true)]
	[string] $executable_name,

	[Parameter(Mandatory=$false)]
	[string] $debug_with_visual_studio
)

if (!(Test-Path -Path $executable_name)) {
    Write-Host "ERROR: Can't find exe, building..." -ForegroundColor Red
    ./build_example.ps1
    if (debug_with_visual_studio -eq "vs") {
        devenv $executable_name
    } else {
        & "raddbg" $executable_name
    }
} else {
    ./vars.ps1
    if (debug_with_visual_studio -eq "vs") {
        devenv $executable_name
    } else {
        & "raddbg" $executable_name
    }
}