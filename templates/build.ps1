using module "./c-build/module/Project.psm1"

param(
    [Parameter(Mandatory=$false)]
    [Procedure] $BuildNoCheck
)

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
if ($BuildNoCheck -eq $true) {
    $project.BuildAllProceduresNoCheck($false)
} else {
    $project.BuildAllProcedures($false)
}


$timer.Stop()
Write-Host "|--------------- Build time: $($timer.Elapsed.TotalSeconds)s ---------------|" -ForegroundColor Blue