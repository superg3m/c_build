class BuildProcedure {
    [bool]$should_build_procedure
    [bool]$should_fully_rebuild_project_dependencies

    [string]$name
    [string]$output_name

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