#!/usr/bin/env fish

argparse c/contributors -- $argv
or return

set current_tag (git tag --sort=-creatordate | sed -n 1p)
set previous_tag (git tag --sort=-creatordate | sed -n 2p)
set commits (git log $current_tag...$previous_tag --format='%H')
set breaking_changes (git log --grep='BREAKING CHANGE:' $current_tag...$previous_tag --format='%H')

for commit in $commits
    set message_header (git log --format=%s -n 1 $commit)
    set commit_type (string split ': ' "$message_header" | sed -n 1p)
    set commit_description (string split ': ' "$message_header" | sed -n 2p)
    set short_hash (git log --format=%h -n 1 $commit)
    set long_hash (git log --format=%H -n 1 $commit)
    set commit_link "https://github.com/realiserad/fish-ai/commit/$long_hash"
    set message "$commit_description (in commit [`#$short_hash`]($commit_link))"
    if test "$commit_type" = fix || test "$commit_type" = "fix!"
        set -a fixes (echo -n $message)
    end
    if test "$commit_type" = feat || test "$commit_type" = "feat!"
        set -a feats (echo -n $message)
    end
    if test "$commit_type" = perf || test "$commit_type" = "perf!"
        set -a perfs (echo -n $message)
    end
    if test "$commit_type" = "chore(deps)"
        set -a deps (echo -n $message)
    end
end

echo "# What's new?"

if test "$fixes" != ""
    echo ""
    echo "## 🐛 Bug fixes"
    echo ""
    for fix in $fixes
        echo "- $fix"
    end
end

if test "$feats" != ""
    echo ""
    echo "## 🌟 New features and improvements"
    echo ""
    for feat in $feats
        echo "- $feat"
    end
end

if test "$perfs" != ""
    echo ""
    echo "## ⚡ Performance improvements"
    echo ""
    for perfs in $perfs
        echo "- $perf"
    end
end

if test "$deps" != ""
    echo ""
    echo "## ⬆ Dependency updates"
    echo ""
    for dep in $deps
        echo "- $dep"
    end
end

if test -n "$breaking_changes"
    echo ""
    echo "## 💥 Breaking changes"
    for commit_hash in $breaking_changes
        set breaking_change (git log -n 1 "$commit_hash" --format="%b" | \
            # Strip the BREAKING CHANGE: prefix
            awk '/^BREAKING CHANGE:/{print substr($0, 18)}' | \
            # Capitalize the first letter in the sentence
            sed 's/^\(.\)/\u\1/' | \
            # Make sure the sentence ends with a dot
            awk '{if (substr($0, length($0))!= ".") $0 = $0 "."; print toupper(substr($0,1,1)) tolower(substr($0,2))}')
        echo ""
        set short_commit_hash (git rev-parse --short "$commit_hash")
        set commit_link "https://github.com/realiserad/fish-ai/commit/$commit_hash"
        echo "$breaking_change See commit [`#$short_commit_hash`]($commit_link) for more details."
    end
end

if set -q _flag_contributors
    echo ""
    echo "## 🙌 Contributors"
    echo ""
    echo "The following developers made this release possible:"
    echo ""
    set contributors (git log $current_tag...$previous_tag --pretty=format:"%an ([%ae](mailto:%ae))" | sort -u)
    for contributor in $contributors
        echo "- $contributor"
    end
end
