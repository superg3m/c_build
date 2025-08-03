#!/usr/bin/env bash

set -e

# Default values
BUILD_TYPE=""
CLEAN=false
BUILD=false
DEBUG=false
RUN=false

# Helper: lowercase
tolower() {
    echo "$1" | tr '[:upper:]' '[:lower:]'
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --build-type)
            shift
            if [[ "$1" != "debug" && "$1" != "release" ]]; then
                echo "Error: --build-type must be 'debug' or 'release'"
                exit 1
            fi
            BUILD_TYPE=$(tolower "$1")
            ;;
        --clean)
            CLEAN=true
            ;;
        --build)
            BUILD=true
            ;;
        --debug)
            DEBUG=true
            ;;
        --run)
            RUN=true
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
    shift
done

# Require build type unless debug is set
if [[ -z "$BUILD_TYPE" && "$DEBUG" != "true" ]]; then
    echo "Error: --build-type must be specified (unless using --debug)"
    exit 1
fi

# Ensure python points to python3 if on Unix
if [[ "$(uname)" != "Windows_NT" ]]; then
    alias python=python3
fi

# Validate temp files (make sure this script is executable and accepts args)
./c_build/validate_temp_files.ps1 "$(basename "$0")"

# Git clone or update
DIRECTORY_PATH="./c_build"
REPO_URL="https://github.com/superg3m/c_build.git"
if [[ ! -d "$DIRECTORY_PATH" ]]; then
    echo "Directory does not exist. Cloning the repository..."
    git clone "$REPO_URL"
else
    pushd "$DIRECTORY_PATH" > /dev/null
    git fetch origin -q
    git reset --hard origin/main -q
    git pull -q
    popd > /dev/null
fi

# CLEAN
if [[ "$CLEAN" == true ]]; then
    python -B -m c_build_script --execution_type "CLEAN" --build_type "$BUILD_TYPE"
fi

# BUILD
if [[ "$BUILD" == true ]]; then
    python -B -m c_build_script --execution_type "BUILD" --build_type "$BUILD_TYPE"
fi

# DEBUG
if [[ "$DEBUG" == true ]]; then
    python -B -m c_build_script --execution_type "BUILD" --build_type "debug"
    python -B -m c_build_script --execution_type "DEBUG" --build_type "debug"
fi

# RUN
if [[ "$RUN" == true ]]; then
    python -B -m c_build_script --execution_type "RUN" --build_type "$BUILD_TYPE"
fi
