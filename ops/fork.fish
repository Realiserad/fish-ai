#!/usr/bin/env fish

argparse 'u/username=' -- $argv
or return

if not set -q _flag_username
    echo "Please provide a GitHub username using the --username flag."
    return 1
end

set real_name (git config --get user.name)
set email (git config --get user.email)

grep -ril realiserad/fish-ai . | xargs sed -i "s|realiserad/fish-ai|$_flag_username/fish-ai|gi"
grep -rl 'login: "realiserad"' | xargs sed -i "s|login: \"realiserad\"|login: \"$_flag_username\"|g"
sed -i "s/Bastian Fredriksson/$real_name/g" pyproject.toml
sed -i "s/realiserad@gmail.com/$email/g" pyproject.toml
rm .github/FUNDING.yml
rm -r .github/ISSUE_TEMPLATE
rm .github/workflows/badge-popularity.yaml

echo "@$_flag_username" >.github/CODEOWNERS
rm README.md
