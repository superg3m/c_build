class Procedure {
    [string]$directory

    [string]$compiler

    [bool]$should_build_executable = $false
    [bool]$should_build_static_lib = $false
    [bool]$should_build_dynamic_lib = $false


    [string]$output_name
    [string]$compile_time_defines
    [string]$include_paths
    [string]$source_paths
    [string]$additional_libs

    BuildProcedure ([string]$build_directory, [string]$compiler_type. [PSCustomObject]$jsonData) {
        $this.directory = $build_directory

        $this.compiler = $compiler_type

        $this.output_name = $jsonData.'output_name'

        if ($this.output_name -Like "*.exe") {
            $should_build_executable = $true
        } else if ($this.output_name -Like "*.lib" -or $this.output_name -Like "*.a") {
            $this.should_build_static_lib = $true
        } else if ($this.output_name -Like "*.so" -or $this.output_name -Like "*.o" -or $this.output_name -Like "*.dylib") {
            $this.should_build_dynamic_lib = $true
        } else {
            # linux
            $this.should_build_executable = $true
        }

        $this.compile_time_defines = $jsonData.'compile_time_defines'
        $this.include_paths = $jsonData.'include_paths'
        $this.source_paths = $jsonData.'source_paths'
        $this.additional_libs = $jsonData.'additional_libs'
    }

    [bool]IsBuilt() {
        $directoryInfo = Get-ChildItem $this.directory | Measure-Object
        $directoryInfo.count

        return $directoryInfo.count -ne 0
    }

    [void]Build([Project]$project, [bool]$debug = $false) {
        if ($this.should_build_procedure -eq $false) {
            Write-Host "Skipping build procedure: $($this.name)" -ForegroundColor Magenta
            continue
        }

        $scriptPath = -join("./c-build/", $this.compiler_type, "/build_procedure.ps1")
        & $scriptPath -project $project -debug_build $debug -build_procedure $this 
    }

    [void]Clean() {
        Remove-Item -Path "$($this.directory)/*", -Force -ErrorAction SilentlyContinue -Confirm:$false -Recurse
    }

    [void]Execute() {
        if (!$this.IsBuilt()) {
            $this.Build($this.compiler_type)
        }

        if ($debug_with_visual_studio -eq $true) {
            ./vars.ps1
        }

        Push-Location "$($this.directory)"
        & "$($this.output_name)"
        Pop-Location
    }

    [void]Debug() {
        $debug = $true
        $this.Build($this.compiler_type, $debug)

        Push-Location $directory
        if ($debug_with_visual_studio -eq $true) {
            devenv $output_name
        } else {
            & "raddbg" $output_name
        }
        Pop-Location
    }

    [void]PrintBuildProcedure() {
        Write-Host "================================================"
        Write-Host "build_directory: $($this.directory)"
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