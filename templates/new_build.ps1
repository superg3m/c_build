$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$PSNativeCommandUseErrorActionPreference = $true

Push-Location  "./c-build"
git fetch origin -q
git reset --hard origin/main -q
git pull -q
Pop-Location

. ./c-build/utility/utils.ps1

$project = ./c-build/utility/decode_project.ps1

Write-Host "Type: $($result.GetType())"

# $project.Print()

# Write-Host "|--------------- Started Building $($project.name) ---------------|" -ForegroundColor Blue
# $timer = [Diagnostics.Stopwatch]::new()
# $timer.Start()
# 
# $project.BuildProjectDependencies()
# $project.BuildProcedures()
# 
# $timer.Stop()
# Write-Host "|--------------- Build time: $($timer.Elapsed.TotalSeconds)s ---------------|" -ForegroundColor Blue