using module "../module/Procedure.psm1"

param(
    [Parameter(Mandatory=$true)]
    [Procedure] $build_procedure,

    [Parameter(Mandatory=$true)]
    [string] $std_version,

    [Parameter(Mandatory=$true)]
    [bool] $debug_build
)

$build_directory = $build_procedure.directory

$output_name = $build_procedure.output_name
$compile_time_defines = $build_procedure.compile_time_defines

$should_build_static_lib = $build_procedure.should_build_static_lib
$should_build_dynamic_lib = $build_procedure.should_build_dynamic_lib
$should_build_executable = $build_procedure.should_build_executable

$include_paths = $build_procedure.include_paths
$source_paths = $build_procedure.source_paths
$additional_libs = $build_procedure.additional_libs

Write-Host "running [$output_name] build.ps1..." -ForegroundColor Green

./vars.ps1

# Initialize the command with the standard version
$clCommand = "cl /std:$std_version /nologo"

if ($debug_build -eq $true) {
    $clCommand += " /Od"
    $clCommand += " /Zi"
} else {
    $clCommand += " /O2"
}

foreach ($define in $compile_time_defines) {
    #$clCommand += " -D$define"
}

if ($should_build_static_lib -eq $true) {
    $clCommand += " /c"
} else {
    $clCommand += " /Fe$output_name $additional_libs"
}

# $clCommand += " /I$include_paths"
$clCommand += " /FC $source_paths"

if(Test-Path -Path ".\compilation_errors.txt") {
	Remove-Item -Path "./compilation_errors.txt" -Force -Confirm:$false
}

Write-Host "BUILD DIR: $build_directory"

Push-Location $build_directory
    Invoke-Expression "$clCommand | Out-File -FilePath 'compilation_errors.txt' -Append"
    if ($should_build_static_lib -eq $true) {
        Write-Host "OUTPUT NAME: $output_name"

        lib /NOLOGO /OUT:$output_name ".\*.obj" | Out-Default
    }
Pop-Location

./c-build/cl/normalize_path.ps1 -build_procedure $build_procedure