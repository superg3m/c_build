param(
	[Parameter(Mandatory=$true)]
	[string] $executable_name,

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
	[string] $additional_libs_for_example
)


./vars.ps1

if(!(Test-Path -Path ".\examples\cl")) {
    mkdir ".\examples\cl"
}

# Initialize the command with the standard version
$clCommand = "cl /Fe:$executable_name /std:$std_version"

if ($debug_build) {
    $clCommand += " /Od"
} else {
    $clCommand += " /O2"
}

if ($debug_build) {
    $clCommand += " /Zi"
}

#$clCommand += " /I$include_paths"
$clCommand += " /FC ../$source_paths ../../build_cl/$additional_libs_for_example"

if(Test-Path -Path ".\compilation_errors.txt") {
	Remove-Item -Path "./compilation_errors.txt" -Force -Confirm:$false
}

Write-Host "running CKit build.ps1..." -ForegroundColor Green

$timer = [Diagnostics.Stopwatch]::new() # Create a timer
$timer.Start() # Start the timer

Push-Location "./examples/cl"
    Invoke-Expression "$clCommand | Out-File -FilePath '../../compilation_errors.txt' -Append"
Pop-Location

$timer.Stop()
Write-Host "========================================================"
Write-Host "MSVC Elapsed time: $($timer.Elapsed.TotalSeconds)s" -ForegroundColor Blue
Write-Host "========================================================"
Write-Host ""

./normalize_path.ps1