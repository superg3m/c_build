param(
	[Parameter(Mandatory=$true)]
	[string] $compiler_type
)

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

$c_build_version = 0.8

if ($compiler_type -ne "cl" -and $compiler_type -ne "gcc") {
    Write-Error "Compiler type is invalid should be either cl or gcc"
    Break
}

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
    $resolvedContent = $templateContent -replace [regex]::Escape('$compiler_type'), $compiler_type
    $resolvedFilePath = Join-Path -Path $resolvedTemplatesDir -ChildPath $templateFile.Name
    Set-Content -Path $resolvedFilePath -Value $resolvedContent
}
Pop-Location

$modules_path = "./c-build/module"

[Environment]::SetEnvironmentVariable("PSModulePath", $modules_path)

Write-Host "C-Build bootstrap is complete!" -ForegroundColor Green