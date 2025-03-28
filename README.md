# c_build 

`c_build` is a build tool designed to easily and quickly build C/C++ projects and their dependencies. 
It allows you to build C/C++ dependencies, such as libraries that you created or library you are pulling in.

## Features
- Checks for the presence of `c_build.py` to identify project dependencies.
- Supports building dependencies specified in the configuration file.
- Provides scripts for bootstrapping, building, running, debugging, and cleaning the project.

## Dependencies
- python
- powershell
- c|c++ compiler (MSVC (Visual Studio), GCC, CLANG, CC)

## Planned Improvements
- Add a good way to do "./core/*/*.c" where ./core/*/ mean recursively search in that directory (do it on default?)

## Usage
### Scripts
- **Bootstrap:** `./bootstrap.ps1`
- **Build:** `./build.ps1` or `./build.ps1 -debug`
- **Run:** `./run.ps1`
- **Debug:** `./debug.ps1` (Opens the debugger)
- **Clean:** `./clean.ps1` (Cleans everything, including dependencies)

## Getting Started
1. Run the bootstrap script to initialize the project.
   - ./bootstrap.ps1

## Dev Notes: (For me)
- Need to do a full rewrite for the 6th time, its almost so good its just rough around the edges
- I mostly need to rethink dependencies the system got more complex than I would like just because 
- of handling dependencies
- REGRESSION Testing has to happen I no longer can keep up with everything in my head
- git clone -b <branch> <remote_repo> (Need to allow you to clone a branch)
- C build DLL watch to recompile, while process is running
- Recompile DLLs when sources change of that procedure.

- Need to add a better way to handle dependencies i'm thinking something like:
```
    project_dependencies = [
        Dependency("ckit", GITHUB_ALWAYS_PULL, "https://github.com/superg3m/ckit.git") 
        Dependency("cj", LOCAL, BUILD_CJ) // BUILD_CJ is a custom function to be ran can be left blank
    ]
```

- This is how you do command line args
project_executable_procedures = [
	"test.exe encode ../asm_input/listing_0038_many_register_mov.asm",
	"8086_instruction_coder.exe decode ../asm_output/listing_0038_many_register_mov"
]

- "compiler_inject_into_args": []

