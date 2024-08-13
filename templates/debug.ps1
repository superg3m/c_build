# This build file has been generated by C-Build
if ($PSVersionTable.Platform -eq "Unix") {
    Set-Alias python python3
}

$current_file = Get-Item "."
$current_filename = $current_file.Name
$template_content = Get-Content -Path "./c-build/templates/$current_filename"

$current_content = Get-Content -Path $current_file.Name
$differences = Compare-Object -ReferenceObject $current_content -DifferenceObject $template_content

if ($differences) {
    Write-Host "Template content for '$current_filename' is out of sync; you must run ./bootstrap.ps1" -ForegroundColor Red
    exit
}

Push-Location  "./c-build"
git fetch origin -q
git reset --hard origin/main -q
git pull -q
Pop-Location

python ./c-build/scripts/debug.py