param(
	[Parameter(Mandatory=$true)]
	[string] $lib_name,

    [Parameter(Mandatory=$false)]
	[string] $compile_time_defines,

    [Parameter(Mandatory=$true)]
	[string] $std_version,

    [Parameter(Mandatory=$true)]
	[bool] $debug_build,

    [Parameter(Mandatory=$false)]
	[string] $include_paths,

    [Parameter(Mandatory=$true)]
	[string] $source_paths,
    
    [Parameter(Mandatory=$false)]
	[string] $libs_example,

    [Parameter(Mandatory=$false)]
	[string] $libs
)

./vars.ps1

if(!(Test-Path -Path ".\build_cl")) {
    mkdir .\build_cl
}

# Initialize the command with the standard version
$clCommand = "cl /std:$std_version"

if ($debug_build) {
    $clCommand += " /Od"
} else {
    $clCommand += " /O2"
}

if ($debug_build) {
    $clCommand += " /Zi"
}

$clCommand += " /I$include_paths"
$clCommand += " /c /FC ../$source_paths $libs_example"

if(Test-Path -Path ".\compilation_errors.txt") {
	Remove-Item -Path "./compilation_errors.txt" -Force -Confirm:$false
}

Write-Host "running CKit build.ps1..." -ForegroundColor Green

$timer = [Diagnostics.Stopwatch]::new() # Create a timer
$timer.Start() # Start the timer

Push-Location ".\build_cl"
    Invoke-Expression "$clCommand | Out-File -FilePath '..\compilation_errors.txt' -Append"
    lib /OUT:$lib_name $libs_example ".\*.obj" | Out-Null
Pop-Location

$timer.Stop()
Write-Host "========================================================"
Write-Host "MSVC Elapsed time: $($timer.Elapsed.TotalSeconds)s" -ForegroundColor Blue
Write-Host "========================================================"
Write-Host ""

./normalize_path.ps1

