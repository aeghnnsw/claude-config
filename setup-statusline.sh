#!/bin/bash

# Setup custom statusline for Claude Code
# Deploys statusline script and configures settings.json

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
STATUSLINE_SCRIPT="$SCRIPT_DIR/templates/statusline-with-tokens.sh"

echo "🚀 Setting up Claude Code statusline..."

# Check if statusline script exists
if [[ ! -f "$STATUSLINE_SCRIPT" ]]; then
    echo "❌ Error: statusline-with-tokens.sh not found in templates/"
    exit 1
fi

# Create ~/.claude directory if needed
mkdir -p "$CLAUDE_DIR"

# Deploy statusline script
echo "📄 Installing statusline script..."
cp "$STATUSLINE_SCRIPT" "$CLAUDE_DIR/statusline-with-tokens.sh"
chmod +x "$CLAUDE_DIR/statusline-with-tokens.sh"

# Update settings.json with statusLine config
echo "📄 Configuring settings.json..."
if [[ -f "$CLAUDE_DIR/settings.json" ]]; then
    # Merge statusLine into existing settings
    jq '.statusLine = {"type": "command", "command": "bash '"$CLAUDE_DIR"'/statusline-with-tokens.sh"}' \
        "$CLAUDE_DIR/settings.json" > "$CLAUDE_DIR/settings.json.tmp"
    mv "$CLAUDE_DIR/settings.json.tmp" "$CLAUDE_DIR/settings.json"
else
    # Create new settings.json
    cat > "$CLAUDE_DIR/settings.json" << EOF
{
  "\$schema": "https://json.schemastore.org/claude-code-settings.json",
  "statusLine": {
    "type": "command",
    "command": "bash $CLAUDE_DIR/statusline-with-tokens.sh"
  }
}
EOF
fi

echo "✅ Statusline configured!"
echo ""
echo "📋 Installed:"
echo "  - $CLAUDE_DIR/statusline-with-tokens.sh"
echo "  - Updated statusLine in settings.json"
echo ""
echo "🔄 Restart Claude Code to apply changes"
