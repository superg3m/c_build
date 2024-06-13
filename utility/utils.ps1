function Update_GitRepo($git_path) {
    Push-Location $git_path
    git fetch origin -q
    git reset --hard origin/main -q
    git pull -q
    Pop-Location
}

function Start_Timer($project_name) {
    Write-Host "|--------------- Started Building $project_name ---------------|" -ForegroundColor Blue
    $timer = [Diagnostics.Stopwatch]::new()
    $timer.Start()
    return $timer
}

function End_Timer($timer) {
    $timer.Stop()
    Write-Host "|--------------- Build time: $($timer.Elapsed.TotalSeconds)s ---------------|" -ForegroundColor Blue
}

function Parse_JsonFile($file_path) {
    if (!(Test-Path -Path $file_path)) {
        throw "Configuration file not found: $file_path"
    }
    $json_object = Get-Content -Path $file_path -Raw

    return ConvertFrom-Json -InputObject $json_object
}

class BuildProcedure {
    [string]$build_directory

    [string]$name

    [bool]$should_build_procedure
    [bool]$should_build_lib
    [bool]$should_execute
    [bool]$is_built

    [string]$output_name
    [string]$compile_time_defines
    [string]$include_paths
    [string]$source_paths
    [string]$additional_libs

    BuildProcedure ([string]$build_directory, [PSCustomObject]$jsonData) {
        $this.build_directory = $build_directory

        $this.name = $jsonData.'$build_procedure_name'

        $this.should_build_procedure = $jsonData.'$should_build_procedure'
        $this.should_build_lib = $jsonData.'$should_build_lib'
        $this.should_execute = $jsonData.'$should_execute'

        $this.output_name = $jsonData.'$output_name'
        $this.compile_time_defines = $jsonData.'$compile_time_defines'
        $this.include_paths = $jsonData.'$include_paths'
        $this.source_paths = $jsonData.'$source_paths'
        $this.additional_libs = $jsonData.'$additional_libs'
    }

    [void]InvokeBuild([string]$compiler_type) {
        if ($this.should_build_procedure -eq $false) {
            Write-Host "Skipping build procedure: $($this.name)" -ForegroundColor Magenta
            continue
        }

        & "../$compiler_type/internal_build.ps1"

        $this.is_built = $true
    }

    [void]InvokeClean([string]$compiler_type) {
        Remove-Item -Path "$($this.build_directory)/*", -Force -ErrorAction SilentlyContinue -Confirm:$false -Recurse

        $this.is_built = $false
    }

    [void]Execute([string]$compiler_type) {
        if ($this.should_execute -eq $false) {
            continue
        }

        Push-Location "$($this.build_directory)"
        & "$($this.output_name)"
        Pop-Location
    }

    [void]Print() {
        Write-Host "================================================"
        Write-Host "build_directory: $($this.build_directory)"
        Write-Host "name: $($this.name)"
        Write-Host "should_build_procedure: $($this.should_build_procedure)"
        Write-Host "should_build_lib: $($this.should_build_lib)"
        Write-Host "should_execute: $($this.should_execute)"
        Write-Host "output_name: $($this.output_name)"
        Write-Host "compile_time_defines: $($this.compile_time_defines)"
        Write-Host "include_paths: $($this.include_paths)"
        Write-Host "source_paths: $($this.source_paths)"
        Write-Host "additional_libs: $($this.additional_libs)"
        Write-Host "================================================"
    }
}

class Project {
    [string]$name

    [bool]$debug_with_visual_studio
    [bool]$should_fully_rebuild_project_dependencies

    [string[]]$project_dependencies_to_build
    [string]$std_version

    [BuildProcedure[]]$build_procedures

    Project ([PSCustomObject]$jsonData) {
        $this.name = $jsonData.'$project_name'

        $this.debug_with_visual_studio = $jsonData.'$debug_with_visual_studio'
        $this.should_fully_rebuild_project_dependencies = $jsonData.'$should_fully_rebuild_project_dependencies'

        $this.project_dependencies_to_build = $jsonData.'$project_dependencies_to_build'
        $this.std_version = $jsonData.'$std_version'

        $this.build_procedures = [System.Collections.ArrayList]@()
    }

    [BuildProcedure]addBuildProcedure([BuildProcedure]$build_proc) {
        $this.build_procedures += $build_proc
        return $build_proc
    }

    [void]Print() {
        Write-Host "================== name: $($this.name) ==================" -ForegroundColor Magenta
        Write-Host "debug_with_visual_studio: $($this.debug_with_visual_studio)"
        Write-Host "should_fully_rebuild_project_dependencies: $($this.should_fully_rebuild_project_dependencies)"
        Write-Host "project_dependencies_to_build: $($this.project_dependencies_to_build)"
        Write-Host "std_version: $($this.std_version)"
        foreach ($build_proc in $this.build_procedures) {
            $build_proc.Print()
        }
        Write-Host "================================================" -ForegroundColor Magenta
    }
}