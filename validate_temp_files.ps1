param(
     [Parameter(Mandatory=$true)]
     [string]$current_filename
 )

$template_content = Get-Content -Path "./c_build/templates/$current_filename"
$current_content = Get-Content -Path $current_filename
$differences = Compare-Object -ReferenceObject $current_content -DifferenceObject $template_content

if ($differences) {
    if ($current_filename -eq "bootstrap.ps1") {
        throw "Template content for '$current_filename' is out of sync; you must run ./c_build/bootstrap.ps1"
    } else {
        throw "Template content for '$current_filename' is out of sync; you must run ./bootstrap.ps1"
    }

    exit
}