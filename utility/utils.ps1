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
    return Get-Content -Path $file_path -Raw | ConvertFrom-Json
}

class BuildProcedure {
    [bool]$should_build_procedure
    
    [string]$name
    [string]$output_name

    [bool]$should_fully_rebuild_project_dependencies

    BuildProcedure ($json) {
        $this.name = $json.'$build_procedure_name'

        $this.should_build_procedure = $json.'$should_build_procedure'
        $this.should_fully_rebuild_project_dependencies = $json.'$should_fully_rebuild_project_dependencies'

        $this.output_name = $json.'$output_name'
    }

    BuildProcedure (
        [bool]$should_build_procedure,
        [bool]$should_fully_rebuild_project_dependencies,
        [string]$name,
        [string]$output_name
    ) {
        $this.should_build_procedure = $should_build_procedure
        $this.should_fully_rebuild_project_dependencies = $should_fully_rebuild_project_dependencies
        $this.name = $name
        $this.output_name = $output_name
    }

    [void]InvokeBuild([string]$compiler_type) {
        ../$compiler_type/internal_build.ps1
    }

    [void]Print() {
        Write-Host "name: $($this.name)"
        Write-Host "should_build_procedure: $($this.should_build_procedure)"
        Write-Host "should_fully_rebuild_project_dependencies: $($this.should_fully_rebuild_project_dependencies)"
        Write-Host "output_name: $($this.output_name)"
    }
}

class Project {
    [string]$name

    [bool]$debug_with_visual_studio
    [string[string]]$project_dependencies_to_build
    [string]$std_version

    [BuildProcedure[]]$BuildProcedures

    Project ($json) {
        $this.name = $json.'$project_name'

        $this.debug_with_visual_studio = $json.'$debug_with_visual_studio'
        $this.project_dependencies_to_build = $json.'$project_dependencies_to_build'
        $this.std_version = $json.'$std_version'
    }

    [void]AddBuildProcedure([string]$build_proc) {
        $this.BuildProcedures.Add($build_proc)
    }

    [void]Print() {
        Write-Host "name: $($this.name)"
        Write-Host "should_build_procedure: $($this.should_build_procedure)"
        Write-Host "should_fully_rebuild_project_dependencies: $($this.should_fully_rebuild_project_dependencies)"
        Write-Host "output_name: $($this.output_name)"
    }
}