param(
    [Parameter(Mandatory=$true)]
    [string] $project_name,

    [Parameter(Mandatory=$true)]
    [string] $build_directory,

    [Parameter(Mandatory=$true)]
    [string] $build_json
)

$jsonData = $build_json | ConvertFrom-Json

$output_name = $jsonData.'$output_name'
$build_name = $jsonData.'$build_name'
$build_lib = $jsonData.'$build_lib'

./C-BUILD/cl/build.ps1 -project_name $project_name -build_directory $build_directory -build_json $build_json

Write-Host "running [$project_name - $build_name] run.ps1..." -ForegroundColor Green

Push-Location $build_directory
    if ($build_lib -eq $false) {
        & "./$output_name"
    }
Pop-Location