Push-Location  "./c-build"
git fetch origin -q
git reset --hard origin/main -q
git pull -q
Pop-Location

. ./c-build/utility/utils.ps1

[Project] $project = ./c-build/utility/decode_project.ps1

Write-Host "|--------------- Started Building $project_name ---------------|" -ForegroundColor Blue
$timer = [Diagnostics.Stopwatch]::new()
$timer.Start()

$project.BuildProjectDependencies()
$ptojrvy.InvokeBuildProcedures()

$timer.Stop()
Write-Host "|--------------- Build time: $($timer.Elapsed.TotalSeconds)s ---------------|" -ForegroundColor Blue