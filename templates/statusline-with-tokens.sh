#!/bin/bash

# Read JSON input from stdin
input=$(cat)

# Debug: Save complete JSON to file
echo "$input" > /tmp/claude_statusline_debug.json

# Extract values
current_dir=$(echo "$input" | jq -r '.workspace.current_dir')
model=$(echo "$input" | jq -r '.model.display_name')
total_cost=$(echo "$input" | jq -r '.cost.total_cost_usd // 0')
total_duration=$(echo "$input" | jq -r '.cost.total_duration_ms // 0')

# Extract context window info
input_tokens=$(echo "$input" | jq -r '.context_window.total_input_tokens // 0')
output_tokens=$(echo "$input" | jq -r '.context_window.total_output_tokens // 0')
context_window_size=$(echo "$input" | jq -r '.context_window.context_window_size // 200000')

# Get git info
git_info=$(cd "$current_dir" 2>/dev/null && git branch --show-current 2>/dev/null | sed 's/^/ (/' | sed 's/$/)/' || echo '')

# Format cost - always show cost
cost_info=""
if [ "$total_cost" != "null" ]; then
    cost_display=\$$(printf "%.2f" "$total_cost")
    cost_info=$(printf " \033[33m%s\033[0m" "$cost_display")
fi
# Note: For Claude Max subscribers, cost is typically 0/null, so no cost info is displayed

# Format context usage if available
context_info=""
if [ "$input_tokens" != "0" ] && [ "$input_tokens" != "null" ] && [ "$context_window_size" != "0" ] && [ "$context_window_size" != "null" ]; then
    # Calculate context usage percentage
    context_pct=$(echo "scale=1; $input_tokens * 100 / $context_window_size" | bc -l)
    # Format tokens in K
    input_k=$(echo "scale=1; $input_tokens / 1000" | bc -l | sed 's/^\./0./')
    output_k=$(echo "scale=1; $output_tokens / 1000" | bc -l | sed 's/^\./0./')
    context_info=$(printf " \033[34m%.1fK/%.1fK (%.0f%%)\033[0m" "$input_k" "$output_k" "$context_pct")
fi

# Format duration if significant (over 1 second)
duration_info=""
if [ "$total_duration" != "0" ] && [ "$total_duration" != "null" ]; then
    duration_seconds=$(echo "scale=1; $total_duration / 1000" | bc -l)
    if (( $(echo "$duration_seconds >= 1" | bc -l) )); then
        duration_display=$(echo "$duration_seconds" | sed 's/\.0$//')s
        duration_info=$(printf " \033[35m%s\033[0m" "$duration_display")
    fi
fi

# Output the status line - clean format without line changes
printf "\033[36m%s\033[0m%s \033[32m%s\033[0m%s%s%s" \
    "$(basename "$current_dir")" \
    "$git_info" \
    "$model" \
    "$cost_info" \
    "$context_info" \
    "$duration_info"