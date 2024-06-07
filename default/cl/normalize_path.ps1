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

Write-Host "running [$project_name - $build_name] normalize_path.ps1..." -ForegroundColor Green

$rootPath = $PSScriptRoot

$tempFilePath = "$build_directory/compilation_errors_temp.txt"
$realFilePath = "$build_directory/compilation_errors.txt"

Write-Host $tempFilePath
Write-Host $realFilePath

New-Item -Path $tempFilePath -Force | Out-Null

Get-Content -Path $realFilePath | ForEach-Object {
    $line = $_
    $line = $line -replace [Regex]::Escape($rootPath), ''
    Add-Content -Path $tempFilePath -Value $line
}

Move-Item -Path $tempFile -Destination $realFilePath -Force
Get-Content -Path $realFilePath
Remove-Item -Path $realFilePath