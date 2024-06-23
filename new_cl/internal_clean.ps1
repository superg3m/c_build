. ./c-build/utility/utils.ps1

param(
    [Parameter(Mandatory=$true)]
    [Project] $project
)

$project_name = $project.name

foreach ($build_procedure in $project.build_procedures) {
    $build_procedure_name = $build_procedure.build_directory

    Write-Host "running [$project_name - $build_procedure_name] clean.ps1..." -ForegroundColor Green
    $build_procedure.Clean()
}
