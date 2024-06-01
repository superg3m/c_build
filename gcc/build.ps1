./vars.ps1

$extension = ".c"

if(!(Test-Path -Path ".\ckg")) {
    Write-Host "missing ckg"
    git clone https://github.com/superg3m/ckg.git
} else {
    Set-Location ".\ckg"
    git stash
    git stash drop
    git pull
    Set-Location ..
}

if(!(Test-Path -Path ".\build_gcc")) {
    mkdir .\build_gcc
}

if(Test-Path -Path ".\compilation_errors.txt") {
	Remove-Item -Path "./compilation_errors.txt" -Force -Confirm:$false
}

Write-Host "running CKit build.ps1..." -ForegroundColor Green

$timer = [Diagnostics.Stopwatch]::new() # Create a timer
$timer.Start() # Start the timer

Set-Location ".\build_gcc"
# g++ -c -std=c++17 -g "../source/core/*.c"
# ar rcs CKit.lib ".\*.o"
Set-Location ..
$timer.Stop()
Write-Host "G++ Elapsed time: $($timer.Elapsed.TotalSeconds)s" -ForegroundColor Blue
Write-Host "========================================================"
Write-Host ""

./normalize_path.ps1

