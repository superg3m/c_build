# This build file has been generated by C-Build

$executable_name = "test_ckit.exe"
$debug_with_visual_studio = $false
$compile_time_defines = ""


$std_version = "c11"
$debug_build = $true
$generate_object_files = $false

$include_paths = ""
$source_paths = "./source"
$lib_paths = ""
$libs = ""

Push-Location  ".\C-BUILD"
git stash
git stash drop
git pull
Pop-Location



./C-BUILD/$preset/$compiler_type/debug.ps1 `
    -executable_name $executable_name `
    -debug_with_visual_studio $debug_with_visual_studio `
    -compile_time_define $compile_time_define `
    -std_version $std_version `
    -debug_build $debug_build `
    -generate_object_files $generate_object_files `
    -include_paths $include_paths `
    -source_paths $source_paths `
    -lib_paths $lib_paths `
    -libs $libs
