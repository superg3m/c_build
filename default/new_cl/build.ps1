param(
    [Parameter(Mandatory=$true)]
    [string] $build_json,

    [Parameter(Mandatory=$false)]
    [bool] $debug_build
)

$jsonData = $build_json | ConvertFrom-Json

$lib_name = $jsonData.'$lib_name'
$executable_name = $jsonData.'$executable_name'
$compile_time_defines = $jsonData.'$compile_time_defines'
$std_version = $jsonData.'$std_version'
$build_lib = $jsonData.'$build_lib'
$generate_object_files = $jsonData.'$generate_object_files'
$include_paths = $jsonData.'$include_paths'
$source_paths = $jsonData.'$source_paths'
$additional_libs = $jsonData.'$additional_libs_for_build'

./vars.ps1

# Initialize the command with the standard version
$clCommand = "cl /std:$std_version"

if ($debug_build -eq $true) {
    $clCommand += " /Od"
} else {
    $clCommand += " /O2"
}

if ($debug_build -eq $true) {
    $clCommand += " /Zi"
}

foreach ($define in $compile_time_defines) {
    #$clCommand += " -D$define"
}

if ($generate_object_files -or $build_lib -eq $true) {
    $clCommand += " /c"
} else {
    $clCommand += " /Fe$executable_name"
}

# $clCommand += " /I$include_paths"
$clCommand += " /FC ../$source_paths $additional_libs"

if(Test-Path -Path ".\compilation_errors.txt") {
	Remove-Item -Path "./compilation_errors.txt" -Force -Confirm:$false
}

Write-Host "running CKit build.ps1..." -ForegroundColor Green

$timer = [Diagnostics.Stopwatch]::new()
$timer.Start()

Push-Location ".\build_cl"
    Invoke-Expression "$clCommand | Out-File -FilePath '..\compilation_errors.txt' -Append"
    if ($build_lib -eq $true) {
        lib /OUT:$lib_name $additional_libs_for_build ".\*.obj" | Out-Null
    }
Pop-Location

$timer.Stop()
Write-Host "========================================================"
Write-Host "MSVC Elapsed time: $($timer.Elapsed.TotalSeconds)s" -ForegroundColor Blue
Write-Host "========================================================"
Write-Host ""

./normalize_path.ps1

