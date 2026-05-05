#!/usr/bin/env fish

if ! type -q pip-weigh
    echo "❌ 'pip-weigh' is not installed."
    echo "Install using 'pip install pip-weigh'."
    exit 1
end

if ! type -q uv-packsize
    echo "❌ 'uv-packsize' is not installed."
    echo "Install using 'pip install uv-packsize'."
    exit 1
end

# Summarise the size of each dependency in a table
pip-weigh --platform linux (python3 -c "import toml; print('\n'.join(toml.load('pyproject.toml')['project']['dependencies']))")

# Calculate the total size in MB when installed using uv
uv-packsize --bin --python (yq '.jobs.python-tests.strategy.matrix.python-version[-1]' .github/workflows/python-tests.yaml) . | grep 'Total size' | awk '{print $3}'
