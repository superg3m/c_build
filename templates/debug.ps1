# This build file has been generated by C-Build
Set-Alias python python3

Push-Location  "./c-build"
git fetch origin -q
git reset --hard origin/main -q
git pull -q
Pop-Location

python ./c-build/scripts/debug.py