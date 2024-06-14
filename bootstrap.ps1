param(
	[Parameter(Mandatory=$true)]
	[string] $compiler_type
)

Push-Location  "./c-build"
git fetch origin -q
git reset --hard origin/main -q
git pull
Pop-Location

if ($compiler_type -ne "cl" -and $compiler_type -ne "gcc") {
    Write-Error "Compiler type is invalid should be either cl or gcc"
    Break
}

# Preset can either be default, ckit or ckg
# if you enter default its not going to give you ckit or anythign its just goint ot make building and compiling easy

if(!(Test-Path -Path "./source")) {
    Write-Host "Creating source Directory"
    mkdir ./source
}

if(!(Test-Path -Path "./include")) {
    Write-Host "Creating include Directory"
    mkdir ./include
}

if(!(Test-Path -Path "./build_$compiler_type")) {
    Write-Host "Creating build_$compiler_type Directory"
    mkdir "./build_$compiler_type" > $null
}

###################################################

Push-Location "./c-build"
$templatesDir = "./templates"
$resolvedTemplatesDir = "../"

$templateFiles = Get-ChildItem -Path $templatesDir -File

$configFilePath = "c_build_config.json"

Write-Host

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
    $resolvedContent = $templateContent -replace [regex]::Escape('$compiler_type'), $compiler_type
    $resolvedFilePath = Join-Path -Path $resolvedTemplatesDir -ChildPath $templateFile.Name
    Set-Content -Path $resolvedFilePath -Value $resolvedContent
}
Pop-Location

Write-Host "C-Build bootstrap is complete!" -ForegroundColor Green