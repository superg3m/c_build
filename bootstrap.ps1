param(
    [Parameter(Mandatory=$true)]
	[string] $preset,
	[Parameter(Mandatory=$true)]
	[string] $compiler_type
)

if ($preset -eq "default" ) {
    Write-Error "preset is invalid should be either default, ckg, or ckit"
    Break
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

# mkdir ../source
# mkdir ../include
# mkdir ../cl_build
# mkdir ../examples
# mkdir ../examples/cl

###################################################

$templatesDir = "./templates"
$resolvedTemplatesDir = "resolved_templates"

if (-not (Test-Path -Path $resolvedTemplatesDir)) {
    New-Item -ItemType Directory -Path $resolvedTemplatesDir
}

$templateFiles = Get-ChildItem -Path $templatesDir -File

foreach ($templateFile in $templateFiles) {
    $templateContent = Get-Content -Path $templateFile.FullName -Raw
    $resolvedContent = $templateContent -replace [regex]::Escape('$preset'), $preset -replace [regex]::Escape('$compiler_type'), $compiler_type
    $resolvedFilePath = Join-Path -Path $resolvedTemplatesDir -ChildPath $templateFile.Name
    Set-Content -Path $resolvedFilePath -Value $resolvedContent
    Write-Output "Resolved script has been written to $resolvedFilePath"
}

Write-Output "C-Build bootstrap is complete!" -ForegroundColor Green