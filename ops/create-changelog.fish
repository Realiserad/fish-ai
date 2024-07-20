#!/usr/bin/env fish

set current_tag (git tag --sort=-creatordate | sed -n 1p)
set previous_tag (git tag --sort=-creatordate | sed -n 2p)
set commits (git log $current_tag...$previous_tag --format='%H')

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
    if test "$commit_type" = "chore(deps)" || test "$commit_type" = "chore(deps)!"
        set -a deps (echo -n $message)
    end
end

echo "# What's new?"
echo ""

if test "$fixes" != ""
    echo "## 🐛 Bug fixes"
    echo ""
    for fix in $fixes
        echo "- $fix"
    end
    echo ""
end

if test "$feats" != ""
    echo "## 🌟 New features and improvements"
    echo ""
    for feat in $feats
        echo "- $feat"
    end
    echo ""
end

if test "$perfs" != ""
    echo "## ⚡ Performance improvements"
    echo ""
    for perfs in $perfs
        echo "- $perf"
    end
    echo ""
end

if test "$deps" != ""
    echo "## ⬆ Dependency updates"
    echo ""
    for dep in $deps
        echo "- $dep"
    end
    echo ""
end
