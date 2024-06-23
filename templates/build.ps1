using module "./c-build/module/Project.psm1"

Push-Location  "./c-build"
git fetch origin -q
git reset --hard origin/main -q
git pull -q
Pop-Location

$json_config_path = "c_build_config.json"
$jsonData = Parse_JsonFile($json_config_path);

$project = [Project]::new($jsonData, "$compiler_type")

Write-Host "|--------------- Started Building $($project.name) ---------------|" -ForegroundColor Blue
Write-Host "Compiler: $compiler_type"
$timer = [Diagnostics.Stopwatch]::new()
$timer.Start()

$project.BuildAllProjectDependencies()
$project.BuildAllProcedures()

$timer.Stop()
Write-Host "|--------------- Build time: $($timer.Elapsed.TotalSeconds)s ---------------|" -ForegroundColor Blue