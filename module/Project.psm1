using module  "./Procedure.psm1"

function Parse_JsonFile($file_path) {
    if (!(Test-Path -Path $file_path)) {
        throw "Configuration file not found: $file_path"
    }
    
    $json_object = Get-Content -Path $file_path -Raw

    return ConvertFrom-Json -InputObject $json_object
}

class Project {
    [string]$name

    [string]$compiler

    [bool]$debug_with_visual_studio
    [bool]$should_rebuild_project_dependencies

    [string[]]$project_dependency_strings
    [Project[]]$project_dependencies

    [string]$std_version

    [Procedure[]]$build_procedures

    [string]$execute_procedure_string
    [Procedure]$execute_procedure

    Project ([PSCustomObject]$jsonData, [string]$compiler_override) {
        $this.name = $jsonData.'project_name'

        $this.debug_with_visual_studio = $jsonData.'debug_with_visual_studio'

        $this.compiler = $compiler_override

        $this.should_rebuild_project_dependencies = $jsonData.'should_rebuild_project_dependencies'

        $this.project_dependency_strings = $jsonData.'project_dependencies'
        $this.std_version = $jsonData.'std_version'

        $this.build_procedures = [System.Collections.ArrayList]@()
        $this.project_dependencies = [System.Collections.ArrayList]@()

        $this.execute_procedure_string = $jsonData.'execute'

        foreach ($key in $jsonData.PSObject.Properties.Name) {
            $value = $jsonData.$key

            if ($value -is [PSCustomObject]) {
                $build_procedure = [Procedure]::new($key, $this.compiler, $value)
                $null = $this.AddBuildProcedure($build_procedure)
                if ($build_procedure.output_name -eq $this.execute_procedure_string) {
                    $this.execute_procedure = $build_procedure;
                }
            }
        }
    }


    Project ([PSCustomObject]$jsonData, [string]$compiler_override, [bool]$should_rebuild_project_dependencies_override) {
        $this.debug_with_visual_studio = $jsonData.'debug_with_visual_studio'

        $this.compiler = $compiler_override

        $this.should_rebuild_project_dependencies = $should_rebuild_project_dependencies_override;

        $this.project_dependency_strings = $jsonData.'project_dependencies'
        $this.std_version = $jsonData.'std_version'

        $this.build_procedures = [System.Collections.ArrayList]@()
        $this.project_dependencies = [System.Collections.ArrayList]@()

        $this.execute_procedure_string = $jsonData.'execute'

        foreach ($key in $jsonData.PSObject.Properties.Name) {
            $value = $jsonData.$key

            if ($value -is [PSCustomObject]) {
                $build_procedure = [Procedure]::new($key, $this.compiler, $value)
                $null = $this.AddBuildProcedure($build_procedure)
                if ($build_procedure.output_name -eq $this.execute_procedure_string) {
                    $this.execute_procedure = $build_procedure;
                }
            }
        }
    }

    [Project]AddSubProject([Project]$sub_project) {
        $this.project_dependencies += $sub_project
        return $sub_project
    }

    [void]BuildAllProjectDependencies() {
        if (($this.project_dependency_strings.Count -eq 0) -or (!$this.project_dependency_strings[0])) {
            Write-Host "[$($this.name)] depends on nothing" -ForegroundColor Magenta
            return
        }
        Write-Host "[$($this.name)] depends on: " -ForegroundColor Blue
        foreach ($dependency in $this.project_dependency_strings) {
            Write-Host "  - $dependency" -ForegroundColor Blue

            if(!(Test-Path -Path $dependency)) {
                Write-Host "missing $dependency"
                git clone https://github.com/superg3m/$dependency.git
            } else {
                Push-Location $dependency
                git fetch origin -q
                git reset --hard origin/main -q
                git pull -q
                Pop-Location
            }
            
            Push-Location "$dependency"
            if(!(Test-Path -Path "c-build")) {
                git clone "https://github.com/superg3m/c-build.git"
            } else {
                Push-Location  "./c-build"
                git fetch origin -q
                git reset --hard origin/main -q
                git pull -q
                Pop-Location
            }

            ./build.ps1
            
            Pop-Location
        }
        Write-Host ""
    }

    [void]BuildAllProcedures([bool]$debug_mode) {
        foreach ($build_procedure in $this.build_procedures) {
            $build_procedure.Build($this.std_version, $debug_mode)
        }
    }

    [void]CleanAllProcedure() {
        Write-Host "running clean $($this.name)"
        foreach ($build_procedure in $this.build_procedures) {
            $build_procedure.Clean()
        }
    }

    [void]ExecuteProcedure() {
        $this.BuildAllProcedures($false)
        $this.BuildAllProjectDependencies()
        $this.execute_procedure.Execute($this.std_version)
    }

    [void]DebugProcedure() {
        $this.CleanAllProcedure()
        Start-Sleep -Seconds 1
        $this.BuildAllProcedures($true)
        $this.execute_procedure.Debug($this.std_version, $this.debug_with_visual_studio)
    }

    [Procedure]AddBuildProcedure([Procedure]$build_proc) {
        $this.build_procedures += $build_proc
        return $build_proc
    }

    [void]PrintProject() {
        Write-Host "================== name: $($this.name) ==================" -ForegroundColor Magenta
        Write-Host "name: $($this.name)"
        Write-Host "compiler: $($this.compiler)"
        Write-Host "debug_with_visual_studio: $($this.debug_with_visual_studio)"
        Write-Host "should_rebuild_project_dependencies: $($this.should_rebuild_project_dependencies)"
        Write-Host "project_dependencies: $($this.project_dependencies)"
        Write-Host "std_version: $($this.std_version)"
        Write-Host "build_procedures: $($this.build_procedures)"
        Write-Host "================================================" -ForegroundColor Magenta
    }
}