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

if(!(Test-Path -Path "../source")) {
    Write-Host "Creating source Directory"
    mkdir ../source
}

if(!(Test-Path -Path "../include")) {
    Write-Host "Creating include Directory"
    mkdir ../include
}

if(!(Test-Path -Path "$compiler_type")) {
    Write-Host "Creating $compiler_type Directory"
   mkdir "../build_$compiler_type"
}

if(!(Test-Path -Path "../examples")) {
    Write-Host "Creating examples Directory"
    mkdir ../examples
}

if(!(Test-Path -Path "../examples/cl")) {
    Write-Host "Creating examples/cl Directory"
    mkdir ../examples/cl
}

###################################################

Push-Location "./c-build"
$templatesDir = "./templates"
$resolvedTemplatesDir = "../"

if (-not (Test-Path -Path $resolvedTemplatesDir)) {
    New-Item -ItemType Directory -Path $resolvedTemplatesDir
}

$templateFiles = Get-ChildItem -Path $templatesDir -File

$configFilePath = "config.json"

# Read the JSON content
$jsonContent = Get-Content -Raw -Path $jsonFilePath | ConvertFrom-Json

# Iterate over each property in the JSON object
foreach ($property in $jsonContent.PSObject.Properties) {
    $fileName = $property.Name
    $fileContent = $property.Value

    # Check if the file name is not config.json
    if ($fileName -ne "config.json") {
        # Update the file content
        $fileContent | Set-Content -Path $fileName -Force
        Write-Host "Updated $fileName"
    } else {
        Write-Host "Skipped $fileName"
    }
}
Pop-Location

Write-Host "C-Build bootstrap is complete!" -ForegroundColor Green