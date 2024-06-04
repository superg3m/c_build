Write-Host "running CKit clean.bat..." -ForegroundColor Green

Remove-Item -Path ".\build_gcc\*", ".\examples\gcc\*" -Force -ErrorAction SilentlyContinue -Confirm:$false -Recurse