param(
    [Parameter(Mandatory=$true)]
    [string] $project_name,

    [Parameter(Mandatory=$true)]
    [string] $build_directory,

    [Parameter(Mandatory=$true)]
    [string] $build_json
)

$jsonData = $build_json | ConvertFrom-Json

$build_name = $jsonData.'$build_name'

Write-Host "running [$project_name - $build_name] clean.ps1..." -ForegroundColor Green

Remove-Item -Path ".\build_cl\*", -Force -ErrorAction SilentlyContinue -Confirm:$false -Recurse