function Parse_JsonFile($file_path) {
    if (!(Test-Path -Path $file_path)) {
        throw "Configuration file not found: $file_path"
    }
    
    $json_object = Get-Content -Path $file_path -Raw

    return ConvertFrom-Json -InputObject $json_object
}

Push-Location  "./c-build"
git fetch origin -q
git reset --hard origin/main -q
git pull -q
Pop-Location

$c_build_version = 0.9

###################################################

Push-Location "./c-build"
$templatesDir = "./templates"
$resolvedTemplatesDir = "../"

$templateFiles = Get-ChildItem -Path $templatesDir -File

$configFilePath = "c_build.py"
Write-Host

# Check if config.json already exists in the destination directory
$has_exisiting_config = $false
if (Test-Path -Path "../$configFilePath") {
    $has_exisiting_config = $true

    $jsonData = Parse_JsonFile("../$($configFilePath)");
    if ($c_build_version -ne $jsonData.'c_build_version') {
        Pop-Location
        throw "c_build_version is not valid wanted: $c_build_version | got: $($jsonData.'c_build_version')"
    }
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

Write-Host "C-Build bootstrap is complete!" -ForegroundColor Green