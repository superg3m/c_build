param(
    [Parameter(Mandatory=$true)]
    [Project] $project,

    [Parameter(Mandatory=$true)]
    [BuildProcedure] $build_procedure
)

$build_directory = $build_procedure.build_directory

$build_procedure_name = $build_procedure.name

Write-Host "running [$($project.name) -> $build_procedure_name] normalize_path.ps1..." -ForegroundColor Green

$rootPath = $PSScriptRoot

$tempFilePath = "$build_directory/compilation_errors_temp.txt"
$realFilePath = "$build_directory/compilation_errors.txt"

New-Item -Path $tempFilePath -Force | Out-Null

Get-Content -Path $realFilePath | ForEach-Object {
    $line = $_
    $line = $line -replace [Regex]::Escape($rootPath), ''
    Add-Content -Path $tempFilePath -Value $line
}

Move-Item -Path $tempFilePath -Destination $realFilePath -Force
Get-Content -Path $realFilePath