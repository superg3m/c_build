param(
    [Parameter(Mandatory=$true)]
	[string] $preset,
	[Parameter(Mandatory=$true)]
	[string] $compiler_type
)

if ($compiler_type -ne "default" -and $compiler_type -ne "ckg" -and $compiler_type -ne "ckit") {
    Write-Error "Compiler type is invalid should be either cl or gcc"
    Break
}

$build_directory = "../build/$compiler_type"

if ($compiler_type -ne "cl" -and $compiler_type -ne "gcc") {
    Write-Error "Compiler type is invalid should be either cl or gcc"
    Break
}

# Preset can either be default, ckit or ckg
# if you enter default its not going to give you ckit or anythign its just goint ot make building and compiling easy

#mkdir ../source
#mkdir ../include
#mkdir ../cl_build
#mkdir ../examples
#mkdir ../examples/cl


./$preset/$compiler_type/build.ps1
./$preset/$compiler_type/run.ps1
./$preset/$compiler_type/clean.ps1

./$preset/$compiler_type/build_example.ps1
./$preset/$compiler_type/run_example.ps1
./$preset/$compiler_type/clean_example.ps1


