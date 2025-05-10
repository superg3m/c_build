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
- REGRESSION Testing has to happen I no longer can keep up with everything in my head
- Separate folders for Release and Debug


- This is how you do command line args
project_executable_procedures = [
	"test.exe encode ../asm_input/listing_0038_many_register_mov.asm",
	"8086_instruction_coder.exe decode ../asm_output/listing_0038_many_register_mov"
]

- Feature Idea:
- Use file watcher to check if any files have been modified
- Store the cache inside the build directory

- Source files are allowed to be searched recursively with /**/
- source_files = ["../../Source/*.c", "../../Libraries/**/glad.c", "../../source/**/*.cpp"]
