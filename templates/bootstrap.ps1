# Define the directory path and repository URL
$directoryPath = "./c-build"
$repositoryUrl = "https://github.com/superg3m/c-build.git"

# Check if the directory exists
if (-not (Test-Path -Path $directoryPath)) {
    Write-Output "Directory does not exist. Cloning the repository..."
    git clone $repositoryUrl
} else {
    Write-Output "Directory already exists. Skipping clone."
}

# Run the bootstrap script
$bootstrapScriptPath = "$directoryPath/bootstrap.ps1"

if (Test-Path -Path $bootstrapScriptPath) {
    & $bootstrapScriptPath
} else {
    Write-Output "Bootstrap script not found at $bootstrapScriptPath"
}
