# Claude Code Statusline Setup

Custom statusline for Claude Code that displays context window token usage, cost, and session duration.

## What It Shows

```
claude_setup (master) Opus 4.5 $0.52 7.0K/11.9K (4%) 125s
```

- **Directory name** (cyan) - Current working directory
- **Git branch** - Current branch in parentheses
- **Model** (green) - Active Claude model
- **Cost** (yellow) - Session cost in USD
- **Tokens** (blue) - Input/Output tokens in K format + context usage %
- **Duration** (magenta) - Session duration

## Installation

```bash
./setup-statusline.sh
```

This will:
1. Copy `statusline-with-tokens.sh` to `~/.claude/`
2. Configure `statusLine` in `~/.claude/settings.json`

Restart Claude Code to apply changes.

## Repository Structure

```
claude_setup/
├── setup-statusline.sh              # Setup script
├── templates/
│   └── statusline-with-tokens.sh    # Statusline script
└── README.md
```

## Customization

Edit `templates/statusline-with-tokens.sh` and re-run `./setup-statusline.sh`.

The script receives JSON via stdin with:
- `context_window.total_input_tokens` - Input tokens used
- `context_window.total_output_tokens` - Output tokens used
- `context_window.context_window_size` - Total context size
- `cost.total_cost_usd` - Session cost
- `cost.total_duration_ms` - Session duration
- `model.display_name` - Model name
- `workspace.current_dir` - Working directory

## Requirements

- `bash` - Script execution
- `jq` - JSON parsing
- `bc` - Calculations
- `git` - Branch detection

## Note

Hooks are managed separately via the [cc-skills](https://github.com/aeghnnsw/cc-skills) Claude plugin.
