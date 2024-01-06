set command (codify "Print all integers greater than 0 and less than 4.")
@echo "Checking the output of: '$command'"
@test "generate some numbers" (echo (eval "$command")) = "1 2 3"

set command (codify "How can I update Fish AI?")
@test "update this plugin" "$command" = "fisher install realiserad/fish-ai"
