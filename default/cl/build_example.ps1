param(
	[Parameter(Mandatory=$true)]
	[string] $executable_name,

    [Parameter(Mandatory=$true)]
	[string] $std_version,

    [Parameter(Mandatory=$true)]
	[bool] $debug_build ,

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


./vars.ps1

if(!(Test-Path -Path ".\examples\cl")) {
    mkdir ".\examples\cl"
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

$clCommand += " /c /FC /I$include_paths $source_paths /LIBPATH:$lib_paths /link /LIB:$libs"

if(Test-Path -Path ".\compilation_errors.txt") {
	Remove-Item -Path "./compilation_errors.txt" -Force -Confirm:$false
}

Write-Host "running CKit build.ps1..." -ForegroundColor Green

$timer = [Diagnostics.Stopwatch]::new() # Create a timer
$timer.Start() # Start the timer

Push-Location ".\examples\cl"
    Get-ChildItem -Force
    cl /Fe"test_ckg.exe" "./test_ckg.c"
    # Invoke-Expression "$clCommand | Out-File -FilePath '../../compilation_errors.txt' -Append"
Pop-Location

$timer.Stop()
Write-Host "========================================================"
Write-Host "MSVC Elapsed time: $($timer.Elapsed.TotalSeconds)s" -ForegroundColor Blue
Write-Host "========================================================"
Write-Host ""

./normalize_path.ps1