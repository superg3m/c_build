current project is implicit but you can specify other projects that use c-build to rebuild itself

# Searches for all elements in the current directory of the project
the it cds into that directory calls build bingo
test if project has c_build_config.json
projects_dependencies_to_build = ["ckit"]

rebuilding the project shouldalways happen if you run a build procedure for the current project, however build_dependencies can be skipped

{
    "$project_name" : "CKG",

    "$debug_with_visual_studio" : false,

    "./build_cl" : {
        "$should_build_procedure" : true,
        
        "$should_build_lib" : true,
        "$should_fully_rebuild_project_depedencies" : false,
        "$should_execute" : false,

        "$projects_dependencies_to_build" : [""],

        "$output_name" : "ckg.lib",
        "$compile_time_defines" : "",
        "$std_version" : "c11",

        "$include_paths" : "",
        "$source_paths" : "../source/*.c",

        "$additional_libs" : ""
    },

    "./examples/cl" : {
        "$should_build_procedure" : true,

        "$should_build_lib" : false,
        "$should_fully_rebuild_project_depedencies" : false,
        "$should_execute" : true,

        "$build_procedure_name" : "test ckg",
        "$projects_dependencies_to_build" : [""],

        "$output_name" : "test_ckg.exe",
        "$compile_time_defines" : "",
        "$include_paths" : "",
        "$source_paths" : "../test_ckg.c",

        "$std_version" : "c11",

        "$additional_libs" : "../../build_cl/ckg.lib"
    }


}




ok so with build procs what flags are set
- build_procedure
    - specific_build_procedure_directory : {
        "standard flags" : {
            $should_build_lib
            $should_rebuild_procedure (put a file called c_build_procedure.flag in each of the build directories)
            $should_fully_rebuild_project_depedencies : false
            $should_statically_link_CRT : false (if true do /MT if false do /MD, then if its debug build then do /MTd, /MDd)
        },

        "override flags" : { (flags that effect how other project dependencies build)
            - $should_build_lib
            - $should_rebuild_procedure (put a file called c_build_procedure.flag in each of the build directories)
            - $should_fully_rebuild_project_depedencies
            - $should_link_CRT
                - $should_statically_link_CRT
                - $should_statically_link_CRT
        }


        "$build_procedure_name" : "test ckg",
        "$output_name" : "test_ckg.exe",
        "$compile_time_defines" : "",
        "$include_paths" : "",
        "$source_paths" : "../test_ckg.c",
        "$std_version" : "c11",
        "$build_lib" : false,
        "$additional_libs" : "../../build_cl/ckg.lib"



    }



- run_procedure
    - specific_run_procedure
        - $should_run
        - $should_




Next up I think I need to rethink how projects and build_procedures get returned and where they get returned
I Have to be able to decline the output like this:
    $null = function()

Heres what i'm thinking there will be internal scripts that handle this and then discard the output for the user because you won't need it

but you can use it as another fellow interal script. This is how you are going to pass around references to projects and build dependencies


its like 80% of the way there heres what I need to figure out
- The replacing of $compiler_type is not going to work anymore. I think I want to just have an override switch and then force it to build
based on the ChildProject

I also think I will make that distinction of:
    Project 
    - ChildProjects (This should actually contain the information needed to build this project I want the object)

ok it sort of works I need to clean it up a ton and think through this more don't worry I have plenty of time
I really should write those essays tho sometime soon I think I vow to write those essays watching Leo its a perfect time no excuses