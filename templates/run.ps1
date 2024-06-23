Push-Location  "./c-build"
git fetch origin -q
git reset --hard origin/main -q
git pull -q
Pop-Location

. ./c-build/module/utils.ps1

[Project] $project = ./c-build/module/decode_project.ps1

$project.ExecuteProcedures()