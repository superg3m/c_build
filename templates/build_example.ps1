# This build file has been generated by C-Build

$executable_name = ""
$compile_time_defines = ""
$std_version = ""
$debug_build = $false; # compile with debug symbols

$include_paths = ""
$source_paths = "./source"

$lib_paths = ""
$libs = ""

Push-Location  ".\C-BUILD"
git stash
git stash drop
git pull
Pop-Location



./C-BUILD/$preset/$compiler_type/build_example.ps1 `
    -executable_name $executable_name `
    -compile_time_defines $compile_time_defines `
    -std_version $std_version `
    -debug_build $debug_build `
    -include_paths $include_paths `
    -source_paths $source_paths `
    -lib_paths $lib_paths `
    -libs $libs