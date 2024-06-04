./build_example.ps1

Push-Location .\examples\gcc
gcc "..\*.c" -o "ckit_test.exe" -g -L"../../build_gcc" -lckit
& "./ckit_test.exe"
Pop-Location