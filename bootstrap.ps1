Push-Location  "./c_build"
git fetch origin -q
git reset --hard origin/main -q
git pull -q
Pop-Location

###################################################

Push-Location "./c_build"
$templatesDir = "./templates/ps1"
$resolvedTemplatesDir = "../"

$templateFiles = Get-ChildItem -Path $templatesDir -File
$configFilePath = "c_build_script.py"

# Check if config.json already exists in the destination directory
$has_exisiting_config = $false
if (Test-Path -Path "../$configFilePath") {
    $has_exisiting_config = $true
}

foreach ($templateFile in $templateFiles) {
    if ($has_exisiting_config -and $templateFile.Name -eq $configFilePath ) {
        continue
    }

    $templateContent = Get-Content -Path $templateFile.FullName -Raw
    $resolvedFilePath = Join-Path -Path $resolvedTemplatesDir -ChildPath $templateFile.Name
    Set-Content -Path $resolvedFilePath -Value $templateContent
}
Pop-Location

Write-Host "c_build bootstrap is complete!" -ForegroundColor Green