#!/usr/bin/env zsh

zparseopts -D -E -A args c:=contributors

current_tag=$(git tag --sort=-creatordate | sed -n 1p)
previous_tag=$(git tag --sort=-creatordate | sed -n 2p)
commits=$(git log $previous_tag..$current_tag --format='%H')
breaking_changes=$(git log --grep='BREAKING CHANGE:' $previous_tag..$current_tag --format='%H')

fixes=()
feats=()
perfs=()
deps=()

for commit in $commits; do
    message_header=$(git log --format=%s -n 1 $commit)
    commit_type=$(echo "$message_header" | awk -F': ' '{print $1}')
    commit_description=$(echo "$message_header" | awk -F': ' '{print $2}')
    short_hash=$(git log --format=%h -n 1 $commit)
    long_hash=$(git log --format=%H -n 1 $commit)
    commit_link="https://github.com/realiserad/fish-ai/commit/$long_hash"
    message="$commit_description (in commit [#$short_hash]($commit_link))"
    if [[ "$commit_type" =~ ^fix(\([a-z]+\))?!?$ ]]; then
        fixes+=("$message")
    fi
    if [[ "$commit_type" =~ ^feat(\([a-z]+\))?!?$ ]]; then
        feats+=("$message")
    fi
    if [[ "$commit_type" =~ ^perf(\([a-z]+\))?!?$ ]]; then
        perfs+=("$message")
    fi
    if [[ "$commit_type" == "chore(deps)" ]]; then
        deps+=("$message")
    fi
done

echo "# What's new?"

if [[ ${#fixes[@]} -gt 0 ]]; then
    echo ""
    echo "## 🐛 Bug fixes"
    echo ""
    for fix in $fixes; do
        echo "- $fix"
    done
fi

if [[ ${#feats[@]} -gt 0 ]]; then
    echo ""
    echo "## 🌟 New features and improvements"
    echo ""
    for feat in $feats; do
        echo "- $feat"
    done
fi

if [[ ${#perfs[@]} -gt 0 ]]; then
    echo ""
    echo "## ⚡ Performance improvements"
    echo ""
    for perf in $perfs; do
        echo "- $perf"
    done
fi

if [[ ${#deps[@]} -gt 0 ]]; then
    echo ""
    echo "## ⬆ Dependency updates"
    echo ""
    for dep in $deps; do
        echo "- $dep"
    done
fi

if [[ -n "$breaking_changes" ]]; then
    echo ""
    echo "## 💥 Breaking changes"
    for commit_hash in $breaking_changes; do
        breaking_change=$(git log -n 1 "$commit_hash" --format="%b" | awk '/^BREAKING CHANGE:/{print substr($0, 18)}')
        echo ""
        short_commit_hash=$(git rev-parse --short "$commit_hash")
        commit_link="https://github.com/realiserad/fish-ai/commit/$commit_hash"
        echo "$breaking_change See commit [#$short_commit_hash]($commit_link) for more details."
    done
fi

if [[ -n "$args[contributors]" ]]; then
    echo ""
    echo "## 🙌 Contributors"
    echo ""
    echo "The following developers made this release possible:"
    echo ""
    contributors=$(git log $current_tag...$previous_tag --pretty=format:"%an ([%ae](mailto:%ae))" | sort -u)
    for contributor in $contributors; do
        echo "- $contributor"
    done
fi
