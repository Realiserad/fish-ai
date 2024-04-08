#!/usr/bin/env fish

set current_branch (git rev-parse --abbrev-ref HEAD)
set start_hash (git show-ref --hash refs/remotes/origin/$current_branch)
set current_version (grep version pyproject.toml | head -n 1 | cut -d'"' -f2)
set next_version (what-bump --from $current_version $start_hash)
if "$current_version" = "$next_version"
    return
end
sed -i -E "s/version = .+/version = \"$next_version\"/" pyproject.toml
git add pyproject.toml
git commit -C HEAD --amend
