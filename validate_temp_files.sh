#!/bin/bash

# validate_temp_files.sh
# Usage: ./validate_temp_files.sh <current_filename>

set -e

current_filename="$1"
if [ -z "$current_filename" ]; then
  echo "Usage: $0 <current_filename>"
  exit 1
fi

templates_dir="./c_build/templates"
template_file="$templates_dir/$current_filename"
current_file="./$current_filename"

if [ ! -f "$template_file" ]; then
  echo "Template not found: $template_file" >&2
  exit 1
fi

if [ ! -f "$current_file" ]; then
  echo "File to validate not found: $current_file" >&2
  exit 1
fi

# Compare files; diff returns non-zero if differences exist
if ! diff -q "$current_file" "$template_file" > /dev/null; then
  # Yellow text
  YELLOW='\033[0;33m'
  NC='\033[0m'

  if [ "$current_filename" = "bootstrap.sh" ]; then
    echo -e "${YELLOW}Template content for '$current_filename' is out of sync; running ./c_build/bootstrap.sh${NC}"
    bash ./c_build/bootstrap.sh
  else
    echo -e "${YELLOW}Template content for '$current_filename' is out of sync; running ./bootstrap.sh${NC}"
    bash ./bootstrap.sh
  fi

  exit 0
fi
