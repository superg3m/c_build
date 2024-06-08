param(
    [Parameter(Mandatory=$true)]
    [string] $project_name,

    [Parameter(Mandatory=$true)]
    [string] $build_directory,

    [Parameter(Mandatory=$true)]
    [string] $build_json,

    [Parameter(Mandatory=$false)]
    [bool] $run_exe
)

$jsonData = $build_json | ConvertFrom-Json

$output_name = $jsonData.'$output_name'

if (Test-Path -Path "$build_directory/$output_name") {
    Write-Host "Missing $project_name exe | building..."
    ./c-build/$compiler_type/build.ps1 -project_name $project_name -build_directory $key -build_json $jsonValue -run_exe $run_exe
}

Push-Location $build_directory
    if ($build_lib -eq $false -and $run_exe -eq $true) {
        & "./$output_name"
    }
Pop-Location