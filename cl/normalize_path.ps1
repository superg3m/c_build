param(
    [Parameter(Mandatory=$true)]
    [Procedure] $build_procedure
)

$build_directory = $build_procedure.directory

$output_name = $build_procedure.output_name

Write-Host "running [$output_name] normalize_path.ps1..." -ForegroundColor Green

$build_procedure.PrintProcedure()

$rootPath = $PSScriptRoot

$tempFilePath = -join($build_directory, "/compilation_errors_temp.txt")
$realFilePath = -join($build_directory, "/compilation_errors.txt")

Write-Host "PATH: $tempFilePath"
Write-Host "PATH: $realFilePath"


New-Item -Path $tempFilePath -Force | Out-Null

Get-Content -Path $realFilePath | ForEach-Object {
    $line = $_
    $line = $line -replace [Regex]::Escape($rootPath), ''
    Add-Content -Path $tempFilePath -Value $line
}

Move-Item -Path $tempFilePath -Destination $realFilePath -Force
$contents = Get-Content -Path $realFilePath

Write-Host $contents

Remove-Item -Path $realFilePath