param(
    [Parameter(Mandatory=$true)]
    [string] $project_name,

    [Parameter(Mandatory=$true)]
    [string] $build_directory,

    [Parameter(Mandatory=$true)]
    [string] $build_json,

    [Parameter(Mandatory=$true)]
    [bool] $debug_with_visual_studio 
)

$jsonData = $build_json | ConvertFrom-Json

$build_procedure_name = $jsonData.'$build_procedure_name'
$output_name = $jsonData.'$output_name'

Write-Host "running [$project_name - $build_procedure_name] debug.ps1..." -ForegroundColor Green

./c-build/cl/internal_build.ps1 -project_name $project_name -build_directory $build_directory -build_json $build_json -debug_build $true
if ($debug_with_visual_studio -eq $true) {
    ./vars.ps1
}
Push-Location $build_directory
if ($debug_with_visual_studio -eq $true) {
    devenv $output_name
} else {
    & "raddbg" $output_name
}
Pop-Location