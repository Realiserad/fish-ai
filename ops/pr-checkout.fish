#!/usr/bin/env fish

function echo_code --argument-names code
    set_color --italics blue
    echo ""
    echo "  $code"
    echo ""
    set_color normal
end

argparse 'n/pr=' -- $argv
or return

if not set -q _flag_pr
    echo "Error: You must specify the PR number using '--pr'. List open PRs using 'gh pr list --repo realiserad/fish-ai --json number,title'."
    return 1
end

if test -d .git
    git checkout main
    git pull
else
    echo "You need to run this script in the git root directory."
    return 2
end

echo "Checking out PR #$_flag_pr ($(gh pr view $_flag_pr --json title -q .title))."
git fetch origin pull/$_flag_pr/head:pr/$_flag_pr
git checkout pr/$_flag_pr

set -l forked_repo (gh api repos/realiserad/fish-ai/pulls/$_flag_pr --jq '.head.repo.full_name')
set -l remote_branch (gh pr view $_flag_pr --json headRefName -q '.headRefName')
echo "You are all set! Make your changes and push them to the forked repo using:"
echo_code "git push --force git@github.com:$forked_repo pr/$_flag_pr:$remote_branch"
echo "Accept the PR using:"
echo_code "git checkout main; git rebase pr/$_flag_pr; git push"
