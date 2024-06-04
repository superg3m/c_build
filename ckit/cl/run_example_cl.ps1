./build.ps1

if(!(Test-Path -Path ".\examples\cl")) {
    mkdir ".\examples\cl"
}

./build_example.ps1
& $executable
Push-Location -Path ".\examples\cl"
cl /Fe: ".\CKit_Test.exe" /Zi "..\*.c" "..\..\build_cl\CKit.lib"
Pop-Location