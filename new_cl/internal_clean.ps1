param(
    [Parameter(Mandatory=$true)]
    [string] $project_name,

    [Parameter(Mandatory=$true)]
    [string] $build_directory,

    [Parameter(Mandatory=$true)]
    [string] $build_json
)

$jsonData = $build_json | ConvertFrom-Json

$build_procedure_name = $jsonData.'$build_procedure_name'

Write-Host "running [$project_name - $build_procedure_name] clean.ps1..." -ForegroundColor Green

Remove-Item -Path "$build_directory/*", -Force -ErrorAction SilentlyContinue -Confirm:$false -Recurse