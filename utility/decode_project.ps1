param (
    [Parameter(Mandatory=$true)]
    [string]$compiler_override,

    [Parameter(Mandatory=$false)]
    [bool]$should_rebuild_project_dependencies_override
)



. ./c-build/utility/utils.ps1

$json_config_path = "c_build_config.json"
$jsonData = Parse_JsonFile($json_config_path);
$project = [Project]::new($jsonData, $compiler_override, $should_rebuild_project_dependencies_override)


Push-Location  "./c-build"
git fetch origin -q
git reset --hard origin/main -q
git pull -q
Pop-Location

foreach ($key in $jsonData.PSObject.Properties.Name) {
    $value = $jsonData.$key

    if ($value -is [PSCustomObject]) {
        $build_procedure = [BuildProcedure]::new($key, $value)
        $null = $project.AddBuildProcedure($build_procedure)
    }
}

return $project