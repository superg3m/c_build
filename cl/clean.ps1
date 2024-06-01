Write-Host "running CKit clean.bat..." -ForegroundColor Green

Remove-Item -Path ".\build_cl\*", ".\examples\cl\*" -Force -ErrorAction SilentlyContinue -Confirm:$false -Recurse