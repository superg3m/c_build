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

if (Test-Path -Path "$build_directory/$output_name") {
    Write-Host "Missing $project_name exe | building..."
    ./c-build/cl/build.ps1 -project_name $project_name -build_directory $key -build_json $jsonValue
}

Push-Location $build_directory
    & "./$output_name"
Pop-Location