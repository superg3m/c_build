# This build file has been generated by C-Build

$configPath = "config.json"
$jsonData = Get-Content -Path $configPath -Raw | ConvertFrom-Json

$executable_name = $jsonData.'$executable_name'
$compile_time_defines = $jsonData.'$compile_time_defines'
$std_version = $jsonData.'$std_version'
$debug_build = $jsonData.'$debug_build'
$debug_build = $jsonData.'$debug_build'
$generate_object_files = $jsonData.'$generate_object_files'
$include_paths = $jsonData.'$include_paths'
$source_paths = $jsonData.'$source_paths'
$source_example_paths = $jsonData.'$source_example_paths'
$additional_libs_for_build = $jsonData.'$additional_libs_for_build'
$additional_libs_for_example = $jsonData.'$additional_libs_for_example'

Push-Location  ".\C-BUILD"
git stash
git stash drop
git pull
Pop-Location

./C-BUILD/$preset/$compiler_type/run.ps1 `
    -executable_name $executable_name `
    -compile_time_defines $compile_time_defines `
    -compile_time_define $compile_time_define `
    -std_version $std_version `
    -debug_build $debug_build `
    -generate_object_files $generate_object_files `
    -include_paths $include_paths `
    -source_paths $source_paths `
    -source_example_paths $source_example_paths `
    -additional_libs_for_build $additional_libs_for_build `
    -additional_libs_for_example $additional_libs_for_example

