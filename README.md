I really just want 


{
    "$lib_name" : "./ckg.lib",
    "$executable_name" : "test_ckg.exe",
    "$include_paths" : "",
    "$source_paths" : "./source/*.c",
    "$source_example_paths" : "./*.c",

    "$std_version" : "c11",
    "$debug_build" : false,
    "$should_build_lib" : true,
    "$generate_object_files" : false,

    "$additional_libs_for_build" : "",
    "$additional_libs_for_example" : "./ckg.lib"
}

current project is implicit but you can specify other projects that use c-build to rebuild itself

# Searches for all elements in the current directory of the project
the it cds into that directory calls build bingo
test if project has c_build_config.json
projects_dependencies_to_build = ["ckit"]




# Current Project Scope
    - build.ps1
    projects_dependencies_to_build = ["ckit"]
        - Ckit Scope
            - build.ps1
            projects_dependencies_to_build = ["ckg"]
                - Ckg Scope
                    - build.ps1
    - build is resolved


// From the current scope how do you get to the next build directory then it will cd into that directory
{
    "./build_$compiler_type" : {
        "$projects_dependencies_to_build" : ["ckit"],

        "$output_name" : "ckg.lib",
        "$include_paths" : "",
        "$source_paths" : "./source/*.c",

        "$std_version" : "c11",
        "$should_build_lib" : true,
        "$generate_object_files" : false,

        "$additional_libs" : "./ckg.lib"
    },

    "./example/$preset" : {
        "$projects_dependencies_to_build" : [""],

        "$output_name" : "test_ckg.exe",
        "$include_paths" : "",
        "$source_paths" : "../*.c",

        "$std_version" : "c11",
        "$should_build_lib" : true,
        "$generate_object_files" : false,

        "$additional_libs" : "",
    }
}

"$debug_build" : false,
doesn't make any sense it should just force debug build if you are debugging otherwise optimized baby!


{
    "$project_name" : "CKG",

    "$debug_with_visual_studio" : false,
    "build procedures" : {
        "./build_cl" : {
            "$should_build_procedure" : true,
            "$should_procedure_rebuild" : true,
            "$should_fully_rebuild_project_depedencies" : false,

            "$should_build_lib" : true,
            "$should_execute" : false,

            "$build_procedure_name" : "build ckg",
            "$projects_dependencies_to_build" : [""],

            "$output_name" : "ckg.lib",
            "$compile_time_defines" : "",
            "$include_paths" : "",
            "$source_paths" : "../source/*.c",

            "$std_version" : "c11",
            "$build_lib" : true,

            "$additional_libs" : ""
        },

        "./examples/cl" : {
            "$should_build_procedure" : true,
            "$should_procedure_rebuild" : true,
            "$should_fully_rebuild_project_depedencies" : false,

            "$should_build_lib" : false,
            "$should_execute" : true,

            "$build_procedure_name" : "test ckg",
            "$projects_dependencies_to_build" : [""],

            "$output_name" : "test_ckg.exe",
            "$compile_time_defines" : "",
            "$include_paths" : "",
            "$source_paths" : "../test_ckg.c",

            "$std_version" : "c11",
            "$build_lib" : false,

            "$additional_libs" : "../../build_cl/ckg.lib"
        }
    }
}