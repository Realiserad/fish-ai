#!/usr/bin/env fish

# Make sure the Python versions tested in the "Python tests" workflow
# correspond to the compatibility check being performed during the
# installation.

if ! type -q yq
    echo "❌ 'yq' is not installed."
    echo "See https://github.com/mikefarah/yq/#install for installation instructions."
    exit 1
end

set tested_versions (yq '.jobs.python-tests.strategy.matrix.python-version[]' \
    .github/workflows/python-tests.yaml)

source conf.d/fish_ai.fish

if test "$tested_versions" != "$supported_versions"
    echo "Supported versions: '$supported_versions'"
    echo "Tested versions: '$tested_versions'"
    echo "Update the 'supported_versions' variable in the 'conf.d/fish_ai.fish' file."
    exit 1
end
