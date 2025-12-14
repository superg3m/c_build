# File paths
$cacheFilePath = "c_build_vcvars_cache.txt"
$vcvarsallPath = "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvarsall.bat"

# Function to generate cache if it doesn't exist
function Generate_CacheFile {
    # Run vcvarsall.bat and capture environment variables
    $envVars = & cmd /c "call `"$vcvarsallPath`" x64 > NUL && set"

    # Write environment variables to the cache file
    $envVars -split "`r`n" | ForEach-Object {
        $name, $value = $_ -split '=', 2
        Add-Content -Path $cacheFilePath -Value "$name=$value"
    }
    Write-Host "Cache file generated: $cacheFilePath" -ForegroundColor Green
}

# Function to load environment variables from cache
function Load_From_Cache {
    Get-Content $cacheFilePath | ForEach-Object {
        $name, $value = $_ -split '=', 2
        [Environment]::SetEnvironmentVariable($name, $value, [System.EnvironmentVariableTarget]::Process)
    }
    Write-Host "Environment variables loaded from cache." -ForegroundColor Green
}

# Check if the cache file exists
if (Test-Path $cacheFilePath) {
    Load_From_Cache
} else {
    Write-Host "Cache file not found. Generating new cache..." -ForegroundColor Yellow
    Generate_CacheFile
    Load_From_Cache
}
