param(
	[Parameter(Mandatory=$true)]
	[string] $compiler_type,
    [Parameter(Mandatory=$true)]
    [string] $std_version
)

$build_directory = "../build/$compiler_type"

