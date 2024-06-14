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
    [Project]$project

    [string]$build_directory

    [string]$name

    [bool]$should_build_procedure
    [bool]$should_build_lib
    [bool]$should_execute

    [string]$output_name
    [string]$compile_time_defines
    [string]$include_paths
    [string]$source_paths
    [string]$additional_libs

    BuildProcedure ([string]$project_name, [string]$build_directory, [PSCustomObject]$jsonData) {
        $this.project_name = $project_name

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

    [bool]IsBuilt() {
        $directoryInfo = Get-ChildItem $this.build_directory | Measure-Object
        $directoryInfo.count

        return $directoryInfo.count -ne 0
    }

    [void]InvokeBuild([string]$compiler_type) {
        if ($this.should_build_procedure -eq $false) {
            Write-Host "Skipping build procedure: $($this.name)" -ForegroundColor Magenta
            continue
        }

        ./c-build/$compiler_type/internal_build.ps1 -project $this.project
    }

    [void]InvokeClean([string]$compiler_type) {
        Remove-Item -Path "$($this.build_directory)/*", -Force -ErrorAction SilentlyContinue -Confirm:$false -Recurse
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

    [string]$compiler

    [bool]$debug_with_visual_studio
    [bool]$should_rebuild_project_dependencies

    [string[]]$project_dependencies
    [string]$std_version

    [BuildProcedure[]]$build_procedures

    Project ([PSCustomObject]$jsonData, [string]$compiler) {
        $this.name = $jsonData.'$project_name'

        if ($null -eq $compiler) {
            $this.compiler = $jsonData.'$compiler_type'
        } else {
            $this.compiler = $compiler;
        }

        $this.debug_with_visual_studio = $jsonData.'$debug_with_visual_studio'
        $this.should_rebuild_project_dependencies = $jsonData.'$should_rebuild_project_dependencies'

        $this.project_dependencies = $jsonData.'$project_dependencies'
        $this.std_version = $jsonData.'$std_version'

        $this.build_procedures = [System.Collections.ArrayList]@()
    }

    [void]buildProjectDependencies() {
        Write-Host "[$($this.name)] depends on: " -ForegroundColor Blue
        foreach ($dependency in $this.project_dependencies) {
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

            $project_dependency = ./build.ps1 -should_build_project $false
            $is_dependency_built_result = $false

            foreach ($build_procedure in $project_dependency.build_procedures) {
                if ($this.should_rebuild_project_dependencies -eq $true) {
                    $build_procedure.InvokeClean()
                    continue
                }

                $is_dependency_built_result = $build_procedure.IsBuilt()
                if ($is_dependency_built_result -eq $false) {
                    break
                }
            }


            
            if ($is_dependency_built_result -eq $true) {
                Write-Host "$dependency Depedency Already Build Skipping..." -ForegroundColor Magenta
            } else {
                ./c-build/bootstrap.ps1 -compiler_type $this.compiler_type
                $project_dependency = ./build.ps1 -compiler_type_override $this.compiler_type
                New-Item -Path "c_build_is_build.flag" > $null
            }
            
            Pop-Location
        }
        Write-Host ""
    }

    [BuildProcedure]addBuildProcedure([BuildProcedure]$build_proc) {
        $this.build_procedures += $build_proc
        return $build_proc
    }

    [void]Print() {
        Write-Host "================== name: $($this.name) ==================" -ForegroundColor Magenta
        Write-Host "debug_with_visual_studio: $($this.debug_with_visual_studio)"
        Write-Host "should_rebuild_project_dependencies: $($this.should_rebuild_project_dependencies)"
        Write-Host "project_dependencies: $($this.project_dependencies)"
        Write-Host "std_version: $($this.std_version)"
        foreach ($build_proc in $this.build_procedures) {
            $build_proc.Print()
        }
        Write-Host "================================================" -ForegroundColor Magenta
    }
}