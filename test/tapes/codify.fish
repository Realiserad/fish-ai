set command (_fish_ai_codify "Print all integers greater than 0 and less than 4")
@echo "Checking the output of: '$command'"
@test "generate some numbers" (echo (eval "$command")) = "1 2 3"

set command (_fish_ai_codify "Pull the alpine container using docker")
@test "run a shell script" "$command" = "docker pull alpine"
