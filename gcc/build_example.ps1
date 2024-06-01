./build.ps1

if(!(Test-Path -Path ".\examples\cl")) {
    mkdir ".\examples\cl"
}

if(!(Test-Path -Path ".\examples\gcc")) {
    mkdir ".\examples\gcc"
}

Push-Location -Path ".\examples\gcc"
gcc "..\*.c" -o "CKit_Test.exe" -g -L"../../build_gcc" -lCKit
".\CKit_Test.exe"
Pop-Location