using module "./c-build/module/Project.psm1"

Push-Location  "./c-build"
git fetch origin -q
git reset --hard origin/main -q
git pull -q
Pop-Location

$json_config_path = "c_build_config.json"
$jsonData = Parse_JsonFile($json_config_path);

$project = [Project]::new($jsonData, "$compiler_type")

$project.ExecuteProcedure()