Import-Module -Name ./internal_build_procedure.psm1

class Project {
    [string]$name
    [bool]$should_debug_with_visual_studio

    [bool]$should_fully_rebuild_project_depedencies
    [string[]]$projects_dependencies_to_build

    [BuildProcedure[]]$build_procedures

    Project ([string]$project_name, [string]$should_debug_with_visual_studio, [int]$should_fully_rebuild_project_depedencies) {
        $this.name = $project_name
        $this.should_debug_with_visual_studio = $should_debug_with_visual_studio
        $this.$should_fully_rebuild_project_depedencies = $should_fully_rebuild_project_depedencies
    }

    [void]addBuildProcedure([BuildProcedure]build_procedure) {
        $build_procedures.Add(build_procedure)
    }

    [void]DisplayInfo() {
        Write-Host "Name: $($this.FirstName) $($this.LastName), Age: $($this.Age)"
    }
}