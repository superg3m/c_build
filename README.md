# c_build 

`c_build` is a tool designed to easily and quickly build C projects and their dependencies. 
It allows you to build C dependencies, such as libraries, that you have created.
The project is moving towards using CMake for better organization and cross-platform support.

- [ ] ADD SOMETHING TO THE CONFIG THAT STOPS IT FROM PULLING TO MAKE SURE DEPENDENCIES ARE UP TO DATE.
   - git_pull_dependencies = true

## Features
- Checks for the presence of `c_build.py` to identify project dependencies.
- Supports building dependencies specified in the configuration file.
- Provides scripts for bootstrapping, building, running, debugging, and cleaning the project.

## Dependencies
- python
- powershell
- c compiler (MSVC, GCC, CLANG, CC)

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
- Add a way to easily get started some type of template

- This is how you do command line args
project_executable_procedures = [
	"test.exe encode ../asm_input/listing_0038_many_register_mov.asm",
	"8086_instruction_coder.exe decode ../asm_output/listing_0038_many_register_mov"
]

- "compiler_inject_into_args": [],