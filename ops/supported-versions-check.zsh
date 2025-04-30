#!/usr/bin/env zsh

# Make sure the Python versions tested in the "Python tests" workflow
# correspond to the compatibility check being performed during the
# installation.

if ! command -v yq &> /dev/null
then
    echo "❌ 'yq' is not installed."
    echo "See https://github.com/mikefarah/yq/#install for installation instructions."
    exit 1
fi

tested_versions=$(yq '.jobs.python-tests.strategy.matrix.python-version[]' \
    .github/workflows/python-tests.yaml)

source conf.d/fish_ai.zsh

if [ "$tested_versions" != "$supported_versions" ]; then
    echo "Supported versions: '$supported_versions'"
    echo "Tested versions: '$tested_versions'"
    echo "Update the 'supported_versions' variable in the 'conf.d/fish_ai.zsh' file."
    exit 1
fi
