param(
     [Parameter(Mandatory=$true)]
     [string]$current_filename
 )

$template_content = Get-Content -Path "./c-build/templates/$current_filename"

$current_content = Get-Content -Path $current_file.Name
$differences = Compare-Object -ReferenceObject $current_content -DifferenceObject $template_content

if ($differences) {
    Write-Host "Template content for '$current_filename' is out of sync; you must run ./bootstrap.ps1" -ForegroundColor Red
    exit
}