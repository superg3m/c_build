Push-Location  "./c-build"
git fetch origin -q
git reset --hard origin/main -q
git pull
Pop-Location

. ./c-build/utility/utils.ps1

[Project] $project = ./c-build/utility/decode_project.ps1

$project.ExecuteProcedures()