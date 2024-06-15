#!/usr/bin/env fish

if ! type -q what-bump
    echo "❌ 'what-bump' is not installed."
    echo "See https://docs.rs/crate/what-bump/latest for installation instructions."
    exit 1
end

set current_branch (git rev-parse --abbrev-ref HEAD)
set start_hash (git show-ref --hash refs/remotes/origin/$current_branch)
set current_version (git show $start_hash:pyproject.toml | grep version | head -n 1 | cut -d'"' -f2)
set next_version (what-bump --from $current_version $start_hash)
if test "$current_version" = "$next_version"
    exit 0
end

sed -i -E "s/^version = .+/version = \"$next_version\"/" pyproject.toml

echo "🎉 The version has been bumped from $current_version to $next_version."
echo "To add the changes, run the following commands:"
echo "  git add pyproject.toml"
echo "  git commit --amend --no-edit"
exit 1
