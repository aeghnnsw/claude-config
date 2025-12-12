# Claude Code Configuration Setup

This repository manages Claude Code configuration templates that can be deployed across multiple machines with automatic path substitution.

## Repository Structure

```
claude_setup/
├── templates/                 # Template configuration files
│   ├── settings.json         # Main Claude settings (with {{HOME}} placeholders)
│   ├── statusline-with-tokens.sh  # Custom statusline (shows tokens, cost, context %)
│   ├── CLAUDE.md            # Global Claude instructions
│   └── hooks/               # Python hook scripts
│       ├── safety_guard.py
│       ├── pre_git_hook.py
│       ├── post_tool_use.py
│       └── system_notification.py
├── sync-from-claude.sh      # Extract current ~/.claude config → templates
├── deploy.sh               # Deploy templates → ~/.claude
└── README.md              # This file
```

## Bi-directional Sync System

### 1. Extract Configuration (Machine → Templates)

When you make changes to your Claude configuration on any machine:

```bash
./sync-from-claude.sh
```

This will:
- Merge `statusLine` from `~/.claude/settings.json` into template (preserves hooks)
- Sync statusline script and hook files
- Convert absolute paths to `{{HOME}}` placeholders
- Exclude machine-specific settings (`enabledPlugins`, `feedbackSurveyState`)
- Preserve untracked files (chat history, cache, etc.)

### 2. Deploy Configuration (Templates → Machine)

To apply templates to a new machine or sync changes:

```bash
./deploy.sh
```

This will:
- Substitute `{{HOME}}` with actual home directory path
- Deploy all configuration files to `~/.claude`
- Set correct permissions on scripts
- Preserve existing untracked data

## Setup Workflow

### Initial Setup on Primary Machine

1. Clone this repository:
   ```bash
   git clone <your-repo-url> ~/Projects/claude_tools/claude_setup
   cd ~/Projects/claude_tools/claude_setup
   ```

2. Extract your current Claude configuration:
   ```bash
   ./sync-from-claude.sh
   ```

3. Commit the templates:
   ```bash
   git add .
   git commit -m "Initial Claude configuration templates"
   git push
   ```

### Setup on Additional Machines

1. Clone the repository:
   ```bash
   git clone <your-repo-url> ~/Projects/claude_tools/claude_setup
   cd ~/Projects/claude_tools/claude_setup
   ```

2. Deploy configuration:
   ```bash
   ./deploy.sh
   ```

3. Restart Claude Code to apply changes

### Syncing Changes

After modifying Claude settings on any machine:

1. **Extract changes**:
   ```bash
   ./sync-from-claude.sh
   ```

2. **Review and commit**:
   ```bash
   git diff  # Review changes
   git add .
   git commit -m "Update configuration from [machine-name]"
   git push
   ```

3. **Deploy to other machines**:
   ```bash
   git pull
   ./deploy.sh
   ```

## Key Features

✅ **Bi-directional sync** - Changes flow both ways
✅ **Path independence** - Works across different user accounts
✅ **Data preservation** - Never touches chat history or cache
✅ **Version controlled** - Full git history of configuration changes
✅ **Selective sync** - Only syncs shared config, excludes machine-specific settings

## Settings Management

**Synced settings** (shared across machines):
- `hooks` - PreToolUse, PostToolUse, Notification hooks
- `statusLine` - Custom statusline configuration

**Excluded settings** (machine-specific):
- `enabledPlugins` - Plugin preferences
- `feedbackSurveyState` - Local UI state
- `alwaysThinkingEnabled` - Personal preference

## Template System

Templates use `{{HOME}}` placeholders for path substitution:

**Template** (`templates/settings.json`):
```json
{
  "command": "uv run {{HOME}}/.claude/hooks/safety_guard.py"
}
```

**Deployed** (`~/.claude/settings.json`):
```json
{
  "command": "uv run /Users/username/.claude/hooks/safety_guard.py"
}
```

## Requirements

- `bash` for running scripts
- `git` for version control
- `sed` for path substitution
- `uv` for Python hook execution
- `jq` and `bc` for statusline calculations

## Troubleshooting

**Script not executable**:
```bash
chmod +x sync-from-claude.sh deploy.sh
```

**Templates out of sync**:
```bash
./sync-from-claude.sh  # Re-extract from current ~/.claude
```

**Deploy failed**:
- Check `~/.claude` exists and is writable
- Verify template files exist in `templates/`
- Check script permissions