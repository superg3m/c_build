# This build file has been generated by C-Build

$executable_name = ""

Push-Location  ".\C-BUILD"
git stash
git stash drop
git pull
Pop-Location

./C-BUILD/$preset/$compiler_type/debug.ps1 $executable_name