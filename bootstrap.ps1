param(
    [Parameter(Mandatory=$true)]
	[string] $preset,
	[Parameter(Mandatory=$true)]
	[string] $compiler_type
)

Push-Location  "./c-build"
git stash
git stash drop
git pull
Pop-Location

if ($preset -eq "default" ) {
    # Do nothing
} elseif ($preset -eq "ckg") {
    if(!(Test-Path -Path "..\ckg")) {
        Write-Host "missing ckg"
        Push-Location  "../"
        git clone https://github.com/superg3m/ckg.git
        Pop-Location
    } else {
        Push-Location  ".\ckg"
        git stash
        git stash drop
        git pull
        Pop-Location
    }
} elseif ($preset -eq "ckit") {
    if(!(Test-Path -Path "..\ckit")) {
        Write-Host "missing ckit"
        Push-Location  "../"
        git clone https://github.com/superg3m/ckit.git
        Pop-Location
    } else {
        Push-Location  ".\ckit"
        git stash
        git stash drop
        git pull
        Pop-Location
    }
} else {
    Write-Error "preset is invalid should be either default, ckg, or ckit"
    Break
}

$build_directory = "../build/$compiler_type"

if ($compiler_type -ne "cl" -and $compiler_type -ne "gcc") {
    Write-Error "Compiler type is invalid should be either cl or gcc"
    Break
}

# Preset can either be default, ckit or ckg
# if you enter default its not going to give you ckit or anythign its just goint ot make building and compiling easy

if(!(Test-Path -Path "./source")) {
    Write-Host "Creating source Directory"
    mkdir ../source
}

if(!(Test-Path -Path "./include")) {
    Write-Host "Creating include Directory"
    mkdir ../include
}

if(!(Test-Path -Path "./build_$compiler_type")) {
    Write-Host "Creating build_$compiler_type Directory"
    mkdir "../build_$compiler_type"
}

if(!(Test-Path -Path "./examples")) {
    Write-Host "Creating examples Directory"
    mkdir ../examples
}

if(!(Test-Path -Path "./examples/$compiler_type")) {
    Write-Host "Creating examples/$compiler_type Directory"
    mkdir ../examples/$compiler_type
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
        Write-Host "Skipping $configFilePath " -ForegroundColor Green
        continue
    }

    $templateContent = Get-Content -Path $templateFile.FullName -Raw
    $resolvedContent = $templateContent -replace [regex]::Escape('$preset'), $preset -replace [regex]::Escape('$compiler_type'), $compiler_type
    $resolvedFilePath = Join-Path -Path $resolvedTemplatesDir -ChildPath $templateFile.Name
    Set-Content -Path $resolvedFilePath -Value $resolvedContent
}
Pop-Location

Write-Host "C-Build bootstrap is complete!" -ForegroundColor Green