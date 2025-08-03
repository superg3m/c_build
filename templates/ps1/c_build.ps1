param (
    [Parameter(Mandatory = $true)]
    [ValidateSet("debug", "release")]
    [string]$BuildType,

    [switch]$Clean,
    [switch]$Build,
    [switch]$DebugMode,
    [switch]$Run
)

if ($PSVersionTable.Platform -eq "Unix") {
    Set-Alias python python3
}

. ./c_build/validate_temp_files.ps1 $MyInvocation.MyCommand.Name

$directoryPath = "./c_build"
$repositoryUrl = "https://github.com/superg3m/c_build.git"
if (-not (Test-Path -Path $directoryPath)) {
    Write-Output "Directory does not exist. Cloning the repository..."
    git clone $repositoryUrl
} else {
    Push-Location $directoryPath
    git fetch origin -q
    git reset --hard origin/main -q
    git pull -q
    Pop-Location
}

$BuildType = $BuildType.ToLower()

if ($Clean) {
    python -B -m c_build_script --execution_type "CLEAN" --build_type $BuildType
}

if ($Build) {
    python -B -m c_build_script --execution_type "BUILD" --build_type $BuildType
}

if ($DebugMode) {
    python -B -m c_build_script --execution_type "BUILD" --build_type "debug"
    python -B -m c_build_script --execution_type "DEBUG" --build_type "debug"
}

if ($Run) {
    python -B -m c_build_script --execution_type "RUN" --build_type $BuildType
}