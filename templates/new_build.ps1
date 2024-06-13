param (
    [Parameter(Mandatory=$false)]
    [bool]$should_build_project
)
. ../utility/utils.ps1

$json_config_path = "c_build_config.json"

Push-Location  "./c-build"
git fetch origin -q
git reset --hard origin/main -q
git pull -q
./bootstrap.ps1
Pop-Location

$jsonData = Parse_JsonFile($json_config_path);

$project = [Project]::new($jsonData)

if ($should_build_project -ne $null) {
    $project.should_fully_rebuild_project_dependencies = $should_build_project
}

$timer = Start_Timer $project.name
foreach ($key in $jsonData.PSObject.Properties.Name) {
    $value = $jsonData.$key

    if ($value -is [PSCustomObject]) {
        $build_procedure = [BuildProcedure]::new($project.name, $key, $value)
        $project.addBuildProcedure($build_procedure).InvokeBuild("$compiler_type")
    }
}

$project.Print()

End_Timer $timer

return $project