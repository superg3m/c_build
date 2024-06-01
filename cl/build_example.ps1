./build.ps1

if(!(Test-Path -Path ".\examples\cl")) {
    mkdir ".\examples\cl"
}

if(!(Test-Path -Path ".\examples\gcc")) {
    mkdir ".\examples\gcc"
}

Push-Location -Path ".\examples\cl"
cl /Fe: ".\CKit_Test.exe" /Zi "..\*.c" "..\..\build_cl\ckit.lib"
Pop-Location