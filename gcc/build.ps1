param(
	[Parameter(Mandatory=$true)]
	[string] $std_version
)

./vars.ps1

$extension = ".c"

if(!(Test-Path -Path ".\ckg")) {
    Write-Host "missing ckg"
    git clone https://github.com/superg3m/ckg.git
} else {
    Push-Location  "./c-build"
    git fetch origin > $null 2>&1
    git reset --hard origin/main > $null 2>&1
    git pull > $null 2>&1
    Pop-Location
}

if(!(Test-Path -Path ".\build_gcc")) {
    mkdir .\build_gcc
}

if(Test-Path -Path ".\compilation_errors.txt") {
	Remove-Item -Path "./compilation_errors.txt" -Force -Confirm:$false
}

Write-Host "running ckit build.ps1..." -ForegroundColor Green

$timer = [Diagnostics.Stopwatch]::new() # Create a timer
$timer.Start() # Start the timer

Set-Location ".\build_gcc"
# -DCUSTOM_PLATFORM_IMPL
g++ -c -std=$std_version -g "../source/core/*$extension"
ar rcs ckit.lib ".\*.o"
Set-Location ..
$timer.Stop()
Write-Host "G++ Elapsed time: $($timer.Elapsed.TotalSeconds)s" -ForegroundColor Blue
Write-Host "========================================================"
Write-Host ""

./normalize_path.ps1

