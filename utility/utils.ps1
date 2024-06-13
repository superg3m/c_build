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

    return $json_object
}

class BuildProcedure {
    [bool]$should_build_procedure
    
    [string]$name
    [string]$output_name

    BuildProcedure ($json) {
        $this.name = $json.'$build_procedure_name'

        $this.should_build_procedure = $json.'$should_build_procedure'

        $this.output_name = $json.'$output_name'
    }

    [void]InvokeBuild([string]$compiler_type) {
        ../$compiler_type/internal_build.ps1
    }

    [void]Print() {
        Write-Host "================================================"
        Write-Host "name: $($this.name)"
        Write-Host "should_build_procedure: $($this.should_build_procedure)"
        Write-Host "output_name: $($this.output_name)"
        Write-Host "================================================"
    }
}

class Project {
    [string]$name

    [bool]$debug_with_visual_studio
    [bool]$should_fully_rebuild_project_dependencies

    [string[]]$project_dependencies_to_build
    [string]$std_version

    [BuildProcedure[]]$BuildProcedures

    Project ([string]$jsonData) {
        Write-Host $jsonData.'$project_name'

        #$this.name = $jsonData.'$project_name'

        #Write-Host "sdfsdfd = $($this.name)" -ForegroundColor Red
        #Write-Host "sdfsdfd = $( $json.'$project_name')" -ForegroundColor Red

        $this.debug_with_visual_studio = $jsonData.'$debug_with_visual_studio'
        $this.should_fully_rebuild_project_dependencies = $jsonData.'$should_fully_rebuild_project_dependencies'

        $this.project_dependencies_to_build = $jsonData.'$project_dependencies_to_build'
        $this.std_version = $jsonData.'$std_version'
    }

    [void]AddBuildProcedure([BuildProcedure]$build_proc) {
        $this.BuildProcedures.Add($build_proc)
    }

    [void]Print() {
        Write-Host "================== name: $($this.name) =================="
        Write-Host "should_build_procedure: $($this.should_build_procedure)"
        Write-Host "debug_with_visual_studio: $($this.debug_with_visual_studio)"
        Write-Host "should_fully_rebuild_project_dependencies: $($this.should_fully_rebuild_project_dependencies)"
        Write-Host "project_dependencies_to_build: $($this.project_dependencies_to_build)"
        Write-Host "std_version: $($this.std_version)"
        foreach ($build_proc in $this.BuildProcedures) {
            $build_proc.Print()
        }
    }
}