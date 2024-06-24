# This build file has been generated by C-Build

using module "./c-build/module/Project.psm1"

Push-Location  "./c-build"
git fetch origin -q
git reset --hard origin/main -q
git pull -q
Pop-Location

$project = $json_config_path = "c_build_config.json"
$jsonData = Parse_JsonFile($json_config_path);
$project = [Project]::new($jsonData, "$compiler_type")

Write-Host "running clean.ps1..." -ForegroundColor Green

$project.CleanAllProcedure()

# ok clean is not quiet right anymore you need to clean all build_procedures