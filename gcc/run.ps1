./build_example.ps1

Push-Location .\examples\gcc
gcc "..\*.c" -o "CKit_Test.exe" -g -L"../../build_gcc" -lCKit
".\CKit_Test.exe"
Pop-Location