#!/usr/bin/fish

function create_completion
    set dir (dirname (status -f))
    set buffer (commandline -b)
    set cursor_pos (commandline -C)
    set completion (echo -n "$buffer" | $dir/create_completion.py $cursor_pos)
    commandline -i $completion
end

