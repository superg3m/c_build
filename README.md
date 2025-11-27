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
- c/c++ compiler (MSVC (Visual Studio), GCC, CLANG, CC)

## Usage
### Scripts
- **Bootstrap:** `./c_build/bootstrap.ps1`
- **c_build.ps1:** `./c_build.ps1 -BuildType debug -Clean -Build -Run` or `./c_build.ps1 -Debugger`

## Getting Started
1. Run the bootstrap script to initialize the project.
   - ./c_build/bootstrap.ps1

## Dev Notes: (For me)
- Add a simple tool that you can call on a .c file and it will give you all the includes recrusively and will even detect circular
includes before compiling. This can be used then to just say ok heres all the source files to make this exe or lib
and within those are all the .h files watch all of these and cache their modified time if cacheable flag is true.
- Make files less cluttered maybe rename c_build to .c_build in order to hide it
- Canonicalize Separate folders for Release and Debug (somehow I would like to make it implicit)
- Caching file modified times (add flag that says, files_to_cache = [])
- Make File globing syntax universal. Example: "./**/*.c, ./**/*.h"


- This is how you do command line args
project_executable_procedures = [
	"test.exe encode ../asm_input/listing_0038_many_register_mov.asm",
	"8086_instruction_coder.exe decode ../asm_output/listing_0038_many_register_mov"
]

- Source files are allowed to be searched recursively with /**/
- `source_files = ["../../Source/*.c", "../../Libraries/**/glad.c", "../../source/**/*.cpp"]`
