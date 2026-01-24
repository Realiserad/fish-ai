#!/usr/bin/env fish

argparse c/contributors -- $argv
argparse s/sponsors -- $argv
or return

set -l current_tag (git tag --sort=-creatordate | sed -n 1p)
set -l previous_tag (git tag --sort=-creatordate | sed -n 2p)
# $A..$B selects all commits in B not in A
set -l commits (git log $previous_tag..$current_tag --format='%H')
set -l breaking_changes (git log --grep='BREAKING CHANGE:' $previous_tag..$current_tag --format='%H')
set -l python_deps (cat pyproject.toml | awk '/dependencies = \[/,/\]/' | sed '1d;$d' | tr -d '", ' | awk -F'==' '{print $1}')

for commit in $commits
    set -l message_header (git log --format=%s -n 1 $commit)
    set -l commit_type (string split ': ' "$message_header" | sed -n 1p)
    set -l commit_description (string split ': ' "$message_header" | sed -n 2p)
    set -l short_hash (git log --format=%h -n 1 $commit)
    set -l long_hash (git log --format=%H -n 1 $commit)
    set -l commit_link "https://github.com/realiserad/fish-ai/commit/$long_hash"
    set -l message "$commit_description (in commit [`#$short_hash`]($commit_link))"
    if string match --regex --quiet 'fix(\([a-z]+\))?!?' "$commit_type"
        set -a fixes (echo -n $message)
    end
    if string match --regex --quiet 'feat(\([a-z]+\))?!?' "$commit_type"
        set -a feats (echo -n $message)
    end
    if string match --regex --quiet 'perf(\([a-z]+\))?!?' "$commit_type"
        set -a perfs (echo -n $message)
    end
    if test "$commit_type" = "chore(deps)"
        # bump <dependency> from <version> to <new_version>
        set -l dependency (string split ' ' "$commit_description" | sed -n 2p)
        set -l new_version (string split ' ' "$commit_description" | sed -n 6p)
        if not contains "$dependency" $python_deps
            continue
        end
        # if a dependency has been bumped more than once, only add the latest bump (first commit in $commits) to the changelog
        if not contains "$dependency" $bumped_deps
            set -a bumped_deps (echo -n "$dependency")
            set -a deps (echo -n "bump $dependency to version $new_version (in commit [`#$short_hash`]($commit_link))")
        end
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
    for perf in $perfs
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
        set -l breaking_change (git log -n 1 "$commit_hash" --format="%b" | \
            # Strip the BREAKING CHANGE: prefix
            awk '/^BREAKING CHANGE:/{print substr($0, 18)}')
        echo ""
        set -l short_commit_hash (git rev-parse --short "$commit_hash")
        set -l commit_link "https://github.com/realiserad/fish-ai/commit/$commit_hash"
        echo "$breaking_change See commit [`#$short_commit_hash`]($commit_link) for more details."
    end
end

if set -q _flag_contributors
    echo ""
    echo "## 🙌 Contributors"
    echo ""
    echo "The following developers made this release possible:"
    echo ""
    set -l contributors (git log $current_tag...$previous_tag --pretty=format:"%an ([%ae](mailto:%ae))" | sort -u)
    for contributor in $contributors
        echo "- $contributor"
    end
end

if set -q _flag_sponsors
    set sponsors (gh api graphql -f query='
        query {
            user(login: "realiserad") {
                sponsorshipsAsMaintainer(first: 100) {
                    nodes {
                        sponsorEntity {
                            ... on User { login }
                            ... on Organization { login }
                        }
                        tier {
                            name
                            monthlyPriceInDollars
                        }
                    }
                }
            }
        }' | jq -r .data.user.sponsorshipsAsMaintainer.nodes[].sponsorEntity.login)
    if test -n "$sponsors"
        echo ""
        echo "## ♥ Sponsors"
        echo ""
        echo "This release is sponsored by:"
        echo ""
        for sponsor in $sponsors
            echo "- @$sponsor"
        end
    end
end
