# c-build

`c-build` is a tool designed to easily and quickly build C projects and their dependencies. 
It allows you to build C dependencies, such as libraries, that you have created.
The project is moving towards using CMake for better organization and cross-platform support.

Going to rewrite this entire thing using ckit, and that will be VERSION 1.0 

## Features
- Searches for all elements in the current directory of the project.
- Checks for the presence of `c_build_config.json` to identify project dependencies.
- Supports building dependencies specified in the configuration file.
- Provides scripts for bootstrapping, building, running, debugging, and cleaning the project.

## Dependencies
- python
- powershell
- c compiler (MSVC, cl only right now)

## Planned Improvements
- Future plans include adding support for `gcc` and `clang`.
- Switching to CMake for better organization and cross-platform compatibility.
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
   ./bootstrap.ps1


Just did a major refactor there are tons of problem to actually fix but it looks like this is actually working for
CL, GCC, CC, CLANG

Resolve build directories make them if you have to!
Resolve dependencies
Resolve procedures in dependencies
Resolve self procedures

I have to make it so that *.c will resolve the source files in python and can't rely on gcc apparently?