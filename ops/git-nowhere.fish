#!/usr/bin/env fish

# Save this as a post-commit hook to use Git without leaking your timezone.
# All commits will be in UTC0.
# Ported from github.com/fionn/git-nowhere

set author_date (git log -1 --date=rfc2822 --format=%ad)
set commit_date (git log -1 --date=rfc2822 --format=%cd)

set unix_author_date (git log -1 --date=unix --format=%ad)
set unix_commit_date (git log -1 --date=unix --format=%cd)

set utc_author_date (date -d @"$unix_author_date" -uR)
set utc_commit_date (date -d @"$unix_commit_date" -uR)

if test "$utc_author_date" = "$author_date" -a "$utc_commit_date" = "$commit_date"
    return 0
end

echo "Setting AuthorDate: $utc_author_date"
echo "Setting CommitDate: $utc_commit_date"

set -x GIT_COMMITTER_DATE $utc_commit_date
git commit --amend --no-edit --no-verify --date="$utc_author_date" 2>/dev/null
