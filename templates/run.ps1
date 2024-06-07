# This build file has been generated by C-Build
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$PSNativeCommandUseErrorActionPreference = $true

$configPath = "config.json"
$jsonData = Get-Content -Path $configPath -Raw | ConvertFrom-Json

$lib_name = $jsonData.'$lib_name'
$output_name = $jsonData.'$executable_name'
$compile_time_defines = $jsonData.'$compile_time_defines'
$std_version = $jsonData.'$std_version'
$debug_build = $jsonData.'$debug_build'
$build_lib = $jsonData.'$build_lib'
$generate_object_files = $jsonData.'$generate_object_files'
$include_paths = $jsonData.'$include_paths'
$source_paths = $jsonData.'$source_paths'
$additional_libs_for_build = $jsonData.'$additional_libs_for_build'

Push-Location  ".\C-BUILD"
git stash
git stash drop
git pull
Pop-Location

./build.ps1
& "./"

# run is complicated because what do you want to run?

