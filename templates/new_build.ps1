param (
    [Parameter(Mandatory=$false)]
    [bool]$should_build_project,

    [Parameter(Mandatory=$false)]
    [bool]$compiler_override,

    [Parameter(Mandatory=$false)]
    [bool]$should_rebuild_project_dependencies_override
)

. ./c-build/utility/utils.ps1

$json_config_path = "c_build_config.json"

$jsonData = Parse_JsonFile($json_config_path);

$project = [Project]::new($jsonData, $compiler_override)

Push-Location  "./c-build"
git fetch origin -q
git reset --hard origin/main -q
git pull -q
Pop-Location

if ($should_build_project -ne $null) { # Acts as an override flag
    $project.should_rebuild_project_dependencies = $should_rebuild_project_dependencies_override
}

$timer = Start_Timer $project.name

$project.buildProjectDependencies()

foreach ($key in $jsonData.PSObject.Properties.Name) {
    $value = $jsonData.$key

    if ($value -is [PSCustomObject]) {
        $build_procedure = [BuildProcedure]::new($project.name, $key, $value)
        if ($should_skip_build -eq $false) {
            $project.addBuildProcedure($build_procedure).InvokeBuild("$compiler_type")
        } else {
            $project.addBuildProcedure($build_procedure)
        }
    }
}


$project.Print()

End_Timer $timer

return $project