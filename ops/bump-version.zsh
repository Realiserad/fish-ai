#!/usr/bin/env zsh

if ! type -q what-bump; then
    echo "❌ 'what-bump' is not installed."
    echo "See https://docs.rs/crate/what-bump/latest for installation instructions."
    exit 1
fi

git fetch --all >/dev/null
start_hash=$(git show-ref --hash refs/remotes/origin/main)
main_version=$(git show $start_hash:pyproject.toml | grep version | head -n 1 | cut -d'"' -f2)
current_version=$(grep version pyproject.toml | head -n 1 | cut -d '"' -f2)
next_version=$(what-bump --from $main_version $start_hash)
if [[ "$main_version" == "$next_version" ]]; then
    exit 0
fi
if [[ "$current_version" == "$next_version" ]]; then
    exit 0
fi

sed -i -E "s/^version = .+/version = \"$next_version\"/" pyproject.toml

echo "🎉 The version has been bumped from $current_version to $next_version."
echo "To accept the change, run the following commands:"
echo "  git add pyproject.toml"
echo "  git commit --amend --no-edit --no-verify"
exit 1
