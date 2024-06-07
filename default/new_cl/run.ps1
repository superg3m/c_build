param(
    [Parameter(Mandatory=$true)]
    [string] $build_json
)

$jsonData = $build_json | ConvertFrom-Json

./C-BUILD/default/cl/build.ps1 -build_json $jsonData

Push-Location ".\build_cl"
    & "./$executable_name"
Pop-Location