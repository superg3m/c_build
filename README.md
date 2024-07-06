# c-build

`c-build` is a tool designed to easily and quickly build C projects and their dependencies. It allows you to build C dependencies, such as libraries, that you have created. The project is moving towards using CMake for better organization and cross-platform support.

## Features
- Searches for all elements in the current directory of the project.
- Checks for the presence of `c_build_config.json` to identify project dependencies.
- Supports building dependencies specified in the configuration file.
- Provides scripts for bootstrapping, building, running, debugging, and cleaning the project.

## Dependencies
- `ckit` (Project dependency to be built)

## Current Status
The project is about 80% complete. Here are some key points:
- The replacement of `$compiler_type` is no longer used. An override switch will force the build based on the `ChildProject`.
- Future plans include adding support for `gcc` and `clang`.
- Ability to clean a dependency chain is in progress.
- The goal is to start with `NoCheck` and then build the necessary checks.

## Planned Improvements
- Switching to CMake for better organization and cross-platform compatibility.
- Writing the `run`, `build`, and `debug` executables in Go.
- Adding a way to compile with debug information without just running `./debug.ps1`.

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
