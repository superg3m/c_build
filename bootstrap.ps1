param(
    [Parameter(Mandatory=$true)]
	[string] $preset,
	[Parameter(Mandatory=$true)]
	[string] $compiler_type
)

if ($preset -ne "default" -and $preset -ne "ckg" -and $preset -ne "ckit") {
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

Write-Output "All templates have been processed and resolved scripts have been written to $resolvedTemplatesDir"