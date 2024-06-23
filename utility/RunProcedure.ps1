class RunProcedure {
    [string]$directory

    [string]$name

    [bool]$should_build_procedure
    [bool]$should_build_lib
    [bool]$should_execute

    [string]$output_name
    [string]$compile_time_defines
    [string]$include_paths
    [string]$source_paths
    [string]$additional_libs

    BuildProcedure ([string]$build_directory, [PSCustomObject]$jsonData) {
        $this.name = $jsonData.'$build_procedure_name'

        $this.build_directory = $build_directory

        $this.should_build_procedure = $jsonData.'$should_build_procedure'
        $this.should_build_lib = $jsonData.'$should_build_lib'
        $this.should_execute = $jsonData.'$should_execute'

        $this.output_name = $jsonData.'$output_name'
        $this.compile_time_defines = $jsonData.'$compile_time_defines'
        $this.include_paths = $jsonData.'$include_paths'
        $this.source_paths = $jsonData.'$source_paths'
        $this.additional_libs = $jsonData.'$additional_libs'
    }

    [bool]IsBuilt() {
        $directoryInfo = Get-ChildItem $this.build_directory | Measure-Object
        $directoryInfo.count

        return $directoryInfo.count -ne 0
    }

    [void]Build([Project]$project, [string]$compiler_type) {
        if ($this.should_build_procedure -eq $false) {
            Write-Host "Skipping build procedure: $($this.name)" -ForegroundColor Magenta
            continue
        }

        $scriptPath = -join("./c-build/", $compiler_type, "/build_procedure.ps1")
        & $scriptPath -project $project -build_procedure $this
    }

    [void]Clean([string]$compiler_type) {
        Remove-Item -Path "$($this.build_directory)/*", -Force -ErrorAction SilentlyContinue -Confirm:$false -Recurse
    }

    [void]Execute([string]$compiler_type) {
        if ($this.should_execute -eq $false) {
            continue
        }

        if (!$this.IsBuilt()) {
            $this.Build($compiler_type)
        }

        Push-Location "$($this.build_directory)"
        & "$($this.output_name)"
        Pop-Location
    }

    [void]PrintBuildProcedure() {
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