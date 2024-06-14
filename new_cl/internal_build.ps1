param(
    [Parameter(Mandatory=$true)]
    [Project] $project,

    [Parameter(Mandatory=$true)]
    [BuildProcedure] $build_procedure,

    [Parameter(Mandatory=$false)]
    [bool] $debug_build
)

. ./c-build/utility/utils.ps1

$build_procedure_name = $build_procedure.name

$output_name = $build_procedure.output_name
$compile_time_defines = $build_procedure.compile_time_defines
$std_version = $project.std_version
$should_build_lib = $build_procedure.should_build_lib
$include_paths = $build_procedure.include_paths
$source_paths = $build_procedure.source_paths
$additional_libs = $build_procedure.additional_libs

Write-Host "running [$($project.name) -> $build_procedure_name] build.ps1..." -ForegroundColor Green

./vars.ps1

# Initialize the command with the standard version
$clCommand = "cl /std:$std_version /nologo"

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

if ($should_build_lib -eq $true) {
    $clCommand += " /c"
} else {
    $clCommand += " /Fe$output_name $additional_libs"
}

# $clCommand += " /I$include_paths"
$clCommand += " /FC $source_paths"

if(Test-Path -Path ".\compilation_errors.txt") {
	Remove-Item -Path "./compilation_errors.txt" -Force -Confirm:$false
}

Push-Location $build_directory
    Invoke-Expression "$clCommand | Out-File -FilePath 'compilation_errors.txt' -Append"
    if ($should_build_lib -eq $true) {
        lib /OUT:$output_name $additional_libs ".\*.obj" | Out-Null
    }
Pop-Location

Write-Host "what the heck????"

./c-build/cl/internal_normalize_path.ps1 -project $project -build_procedure $build_procedure