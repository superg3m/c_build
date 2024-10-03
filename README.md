# C_Build is in a semi unfinished state right now I need to finish the rewrite it works to build
# but scripts like: run.ps1, clean.ps1 or debug.ps1 don't work.


# c_build 

`c_build` is a tool designed to easily and quickly build C projects and their dependencies. 
It allows you to build C dependencies, such as libraries, that you have created.
The project is moving towards using CMake for better organization and cross-platform support.

- [ ] ADD SOMETHING TO THE CONFIG THAT STOPS IT FROM PULLING TO MAKE SURE DEPENDENCIES ARE UP TO DATE.
   - git_pull_dependencies = true
- [ ] Going to rewrite this entire thing using ckit, and that will be VERSION 1.0 (add multi-threading)
  - With multi-threading I should be able to compile multiple dependencies in parallel
    - Provided these dependence have no dependencies of their own or these dependencies are already built

## Features
- Searches for all elements in the current directory of the project.
- Checks for the presence of `c_build.py` to identify project dependencies.
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
   - ./bootstrap.ps1

- [ ] Run
- [x] Build
- [ ] Debug
- [ ] Clean

Eventually procedures that don't depend on anything or 
already have that thing built can be built in parallel with another procedure.


Run the subprocess once then generate a c_build_cache.txt
Then you can just run the build_project(data) and the data comes from the cache this should decrease build time
significantly because I don't have to worry about starting a process and the overhead that incurs. 

c_build_cache_cl.json
c_build_cache_gcc.json
{
    
    build_dir
    proc
    executable

}