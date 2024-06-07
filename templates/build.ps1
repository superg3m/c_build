# This build file has been generated by C-Build
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$PSNativeCommandUseErrorActionPreference = $true

$configPath = "c_build_config.json"
$jsonData = Get-Content -Path $configPath -Raw | ConvertFrom-Json

$project_name = $jsonData.'$project_name'

Push-Location  ".\C-BUILD"
git stash
git stash drop
git pull
Pop-Location

Write-Host "|--------------- Started Building $project_name ---------------|" -ForegroundColor Green
$timer = [Diagnostics.Stopwatch]::new() # Create a timer
$timer.Start() # Start the timer
foreach ($key in $jsonData.PSObject.Properties.Name) {
    $value = $jsonData.$key # value is json


    
    # If the value is an object, iterate over its properties as well
    if ($value -is [PSCustomObject]) {

        if(!(Test-Path -Path $key)) {
            Write-Host "Creating $value Directory"
            mkdir $key
        }

        foreach ($nestedKey in $value.PSObject.Properties.Name) {
            $nestedValue = $value.$nestedKey

            $should_run = $nestedKey.'$should_run'

            if ($should_run -eq $false) {
                break
            }

            if ($nestedValue -is [Array]) {
                Write-Host ""
                if (!$nestedValue) {
                    Write-Host "Depends on Nothing!" -ForegroundColor Blue
                    Write-Host ""
                    continue
                }
                
                Write-Host "Depends on: " -ForegroundColor Blue
                foreach ($element in $nestedValue) {
                    Write-Host "  - $element" -ForegroundColor Blue
                    
                    # Push-Location "$element"
                    # ./C-BUILD/bootstrap.ps1 -preset $preset -compiler_type $compiler_type
                    # ./build.ps1
                    # 
                    # Pop-Location
                }
                Write-Host ""
                Write-Host ""
            }
        }

        # Serialize the $value object to a JSON string
        $jsonValue = $value | ConvertTo-Json -Compress

        ./C-BUILD/$preset/$compiler_type/build.ps1 -project_name $project_name -build_directory $key -build_json $jsonValue
    }
}
$timer.Stop()
Write-Host "|--------------- [Build time: $($timer.Elapsed.TotalSeconds)s] ---------------|" -ForegroundColor Green

