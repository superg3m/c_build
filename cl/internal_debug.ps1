param(
    [Parameter(Mandatory=$true)]
    [string] $project_name,

    [Parameter(Mandatory=$true)]
    [string] $build_directory,

    [Parameter(Mandatory=$true)]
    [string] $build_json
)

$jsonData = $build_json | ConvertFrom-Json

$build_procedure_name = $jsonData.'$build_procedure_name'

Write-Host "running [$project_name - $build_procedure_name] debug.ps1..." -ForegroundColor Green

$debug_with_visual_studio = $jsonData.'$debug_with_visual_studio'

if (!(Test-Path -Path $executable_name)) {
    Write-Host "ERROR: Can't find exe, building..." -ForegroundColor Red

    ./c-build/cl/build.ps1 -build_json $jsonData -debug_build $true
    
    Push-Location "./build_cl"
    if ($debug_with_visual_studio -eq $true) {
        ./vars.ps1
        devenv $executable_name
    } else {
        #& "raddbg" $executable_name
    }
    Pop-Location
} else {
    Push-Location "./build_cl"
    if ($debug_with_visual_studio -eq $true) {
        ./vars.ps1
        devenv $executable_name
    } else {
        #& "raddbg" $executable_name
    }
    Pop-Location
}