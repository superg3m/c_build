param(
    [Parameter(Mandatory=$true)]
	[string] $preset,
	[Parameter(Mandatory=$true)]
	[string] $compiler_type,
    [Parameter(Mandatory=$true)]
    [string] $std_version
)

$build_directory = "../build/$compiler_type"

if ($compiler_type -ne "cl" -and $compiler_type -ne "gcc") {
    Write-Host "Compiler type is invalid should be either cl or gcc"
    Break
}

if ($compiler_type -eq "cl") {
    ./vars.ps1
}

# Preset can either be default, ckit or ckg
# if you enter default its not going to give you ckit or anythign its just goint ot make building and compiling easy


./$compiler_type/build.ps1
./$compiler_type/run.ps1
./$compiler_type/clean.ps1

./$compiler_type/build_example.ps1
./$compiler_type/run_example.ps1
./$compiler_type/clean_example.ps1


