. ../utility/utils.ps1

$json_config_path = "c_build_config.json"

$jsonData = Parse_JsonFile($json_config_path);

$project = [Project]::new($jsonData)

$timer = Start_Timer $project.name
foreach ($key in $jsonData.PSObject.Properties.Name) {
    $value = $jsonData.$key

    if ($value -is [PSCustomObject]) {
        $build_procedure = [BuildProcedure]::new($key, $value)
        $project.addBuildProcedure($build_procedure).InvokeBuild("$compiler_type")
    }
}

$project.Print()

End_Timer $timer