# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Code configuration management system that provides bi-directional synchronization between local `~/.claude` configurations and version-controlled templates. The system uses path placeholders (`{{HOME}}`) to make configurations portable across different machines and user accounts.

## Core Commands

### Bi-directional Sync
- `./sync-from-claude.sh` - Extract current `~/.claude` config → templates (with path conversion)
- `./deploy.sh` - Deploy templates → `~/.claude` (with path substitution)
- `./claude-setup-export.sh` - Legacy export tool that creates standalone installation package

### Testing Workflow
No formal test suite exists. Test by:
1. Running `./sync-from-claude.sh` to capture current config
2. Running `./deploy.sh` on same or different machine
3. Verifying Claude Code loads configuration correctly
4. Testing hooks and statusline functionality

## Architecture

### Template System
- **Templates directory**: Contains portable config files with `{{HOME}}` placeholders
- **Path substitution**: Automated replacement of home directory paths for portability
- **Preservation logic**: Only syncs configuration files, never touches chat history or cache

### Key Components
1. **Settings management** (`templates/settings.json`): Claude Code main configuration including hooks
2. **Statusline script** (`templates/statusline-with-tokens.sh`): Custom status display with git info, model, cost, context usage
3. **Hook system** (`templates/hooks/*.py`): Python scripts for safety guards, git hooks, notifications
4. **Sync scripts**: Bash scripts for bidirectional template management

### Hook Architecture
The system includes several Python hooks executed via `uv`:
- `safety_guard.py` - Pre-tool safety validation
- `pre_git_hook.py` - Git operation preprocessing
- `post_tool_use.py` - Post-tool logging/analysis
- `system_notification.py` - System event notifications

## Configuration Management

### Template Structure
```
templates/
├── settings.json              # Main Claude settings with {{HOME}} placeholders
├── statusline-with-tokens.sh  # Custom statusline script
├── CLAUDE.md                 # Global Claude instructions
└── hooks/                    # Python hook scripts
    ├── safety_guard.py
    ├── pre_git_hook.py
    ├── post_tool_use.py
    └── system_notification.py
```

### Path Handling
- Templates use `{{HOME}}` as placeholder for user home directory
- `sync-from-claude.sh` converts absolute paths to `{{HOME}}` placeholders
- `deploy.sh` substitutes `{{HOME}}` with actual home directory path
- Enables cross-machine and cross-user compatibility

### Dependencies
- `bash` - Script execution
- `sed` - Path substitution
- `jq` - JSON parsing (statusline)
- `bc` - Calculations (statusline)
- `uv` - Python hook execution
- `git` - Version control and branch detection

## Development Practices

### When modifying configurations:
1. Make changes directly in `~/.claude/`
2. Run `./sync-from-claude.sh` to capture changes in templates
3. Commit template changes to version control
4. Deploy to other machines with `./deploy.sh`

### When adding new hooks:
- Place Python scripts in `templates/hooks/`
- Update `templates/settings.json` to reference new hooks
- Use `{{HOME}}` placeholder for any absolute paths
- Test with `uv run` to ensure compatibility

### Statusline customization:
- Modify `templates/statusline-with-tokens.sh`
- Script receives JSON input via stdin with workspace and cost information
- Supports colorized output with bash escape sequences
- Uses `jq` for JSON parsing and `bc` for calculations

## Important Notes
- Never manually edit deployed files in `~/.claude/` for permanent changes
- Always use the sync workflow: modify `~/.claude/` → `sync-from-claude.sh` → commit → `deploy.sh`
- The system preserves chat history, cache, and other non-configuration data
- All hook scripts assume `uv` is available in PATH for Python execution