. ../utility/utils.ps1

$json_config_path = "c_build_config.json"

$jsonData = Parse_JsonFile($json_config_path);


Write-Host $jsonData.'$project_name'

$project = [Project]::new($jsonData)

$timer = Start_Timer $project.name
foreach ($key in $jsonData.PSObject.Properties.Name) {
    $value = $jsonData.$key

    if ($value -is [PSCustomObject]) {
        #$json_convert = $value | ConvertTo-Json
        #$build_procedure = [BuildProcedure]::new($json_convert)
        #$project.AddBuildProcedure($build_procedure);

        #$build_procedure.Print()
    }
}

$project.Print()

End_Timer $timer