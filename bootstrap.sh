#!/bin/bash

# First block: Git update
pushd "./c_build" > /dev/null
git fetch origin -q
git reset --hard origin/main -q
git pull -q
popd > /dev/null

###################################################

# Second block: Copy template files
pushd "./c_build" > /dev/null
templatesDir="./templates/bash"
resolvedTemplatesDir="../"
configFilePath="c_build_script.py"
has_existing_config=false

if [ -f "$resolvedTemplatesDir/$configFilePath" ]; then
    has_existing_config=true
fi

for templateFile in "$templatesDir"/*; do
    filename=$(basename "$templateFile")

    if [ "$has_existing_config" = true ] && [ "$filename" = "$configFilePath" ]; then
        continue
    fi

    cp "$templateFile" "$resolvedTemplatesDir/$filename"
done
popd > /dev/null

echo -e "\033[0;32mc_build bootstrap is complete!\033[0m"
