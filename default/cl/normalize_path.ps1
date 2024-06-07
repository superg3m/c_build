param(
    [Parameter(Mandatory=$true)]
    [string] $project_name,

    [Parameter(Mandatory=$true)]
    [string] $build_json
)

$jsonData = $build_json | ConvertFrom-Json

$build_name = $jsonData.'$build_name'

Write-Host "running [$project_name - $build_name] normalize_path.ps1..." -ForegroundColor Green

$rootPath = $PSScriptRoot
$tempFile = 'compilation_errors_temp.txt'
New-Item -Path $tempFile -Force | Out-Null

Get-Content -Path 'compilation_errors.txt' | ForEach-Object {
    $line = $_
    $line = $line -replace [Regex]::Escape($rootPath), ''
    Add-Content -Path $tempFile -Value $line
}

Move-Item -Path $tempFile -Destination 'compilation_errors.txt' -Force
Get-Content -Path 'compilation_errors.txt'
Remove-Item -Path 'compilation_errors.txt'