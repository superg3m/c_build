param(
     [Parameter(Mandatory=$true)]
     [string]$current_filename
 )

$template_content = Get-Content -Path "./c_build/templates/ps1/$current_filename"
$current_content = Get-Content -Path $current_filename
$differences = Compare-Object -ReferenceObject $current_content -DifferenceObject $template_content

if ($differences) {
    if ($current_filename -eq "bootstrap.ps1") {
        Write-Host "Template content for '$current_filename' is out of sync; running ./c_build/bootstrap.ps1" -ForegroundColor yellow
        ./c_build/bootstrap.ps1
    } else {
        Write-Host "Template content for '$current_filename' is out of sync; running ./bootstrap.ps1" -ForegroundColor yellow
        ./bootstrap.ps1
    }

    exit
}