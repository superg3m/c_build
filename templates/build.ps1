Import-Module "$PSScriptRoot\Procedure.psm1"

Write-Host "TESTINGS: $PSScriptRoot"

Push-Location  "./c-build"
git fetch origin -q
git reset --hard origin/main -q
git pull -q
Pop-Location

function Parse_JsonFile($file_path) {
    if (!(Test-Path -Path $file_path)) {
        throw "Configuration file not found: $file_path"
    }
    
    $json_object = Get-Content -Path $file_path -Raw

    return ConvertFrom-Json -InputObject $json_object
}

$json_config_path = "c_build_config.json"
$jsonData = Parse_JsonFile($json_config_path);

Write-Host "JSON Data: $jsonData" -ForegroundColor Yellow
Write-Host "Compiler Type: $compiler_type" -ForegroundColor Yellow

$project = [Project]::new($jsonData, "$compiler_type")

Write-Host "TESTING: $project" -ForegroundColor Magenta

Write-Host "|--------------- Started Building $($project.name) ---------------|" -ForegroundColor Blue
Write-Host "Compiler: $compiler_type"
$timer = [Diagnostics.Stopwatch]::new()
$timer.Start()

$project.BuildAllProjectDependencies()
$project.BuildAllProcedures()

$timer.Stop()
Write-Host "|--------------- Build time: $($timer.Elapsed.TotalSeconds)s ---------------|" -ForegroundColor Blue