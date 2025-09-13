#!/bin/bash

# Deploy script: templates → ~/.claude
# Applies template configuration to local machine with path substitution

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
TEMPLATES_DIR="$SCRIPT_DIR/templates"

echo "🚀 Deploying Claude configuration to ~/.claude..."

# Check if templates directory exists
if [[ ! -d "$TEMPLATES_DIR" ]]; then
    echo "❌ Error: templates directory not found"
    echo "💡 Run ./sync-from-claude.sh first to create templates"
    exit 1
fi

# Create ~/.claude directory if it doesn't exist
mkdir -p "$CLAUDE_DIR"
mkdir -p "$CLAUDE_DIR/hooks"

# Function to substitute template placeholders with actual paths
substitute_placeholders() {
    local input_file="$1"
    local output_file="$2"

    # Replace {{HOME}} with actual home directory
    sed "s|{{HOME}}|$HOME|g" "$input_file" > "$output_file"
}

# Deploy settings.json
if [[ -f "$TEMPLATES_DIR/settings.json" ]]; then
    echo "📄 Deploying settings.json..."
    substitute_placeholders "$TEMPLATES_DIR/settings.json" "$CLAUDE_DIR/settings.json"
else
    echo "⚠️  Warning: settings.json template not found"
fi

# Deploy statusline script
if [[ -f "$TEMPLATES_DIR/statusline-with-tokens.sh" ]]; then
    echo "📄 Deploying statusline-with-tokens.sh..."
    cp "$TEMPLATES_DIR/statusline-with-tokens.sh" "$CLAUDE_DIR/statusline-with-tokens.sh"
    chmod +x "$CLAUDE_DIR/statusline-with-tokens.sh"
else
    echo "⚠️  Warning: statusline-with-tokens.sh template not found"
fi

# Deploy hook files
if [[ -d "$TEMPLATES_DIR/hooks" ]]; then
    echo "📄 Deploying hook files..."
    for template_file in "$TEMPLATES_DIR/hooks"/*.py; do
        if [[ -f "$template_file" ]]; then
            filename=$(basename "$template_file")
            echo "  - $filename"
            substitute_placeholders "$template_file" "$CLAUDE_DIR/hooks/$filename"
        fi
    done
else
    echo "⚠️  Warning: hooks templates not found"
fi

echo "✅ Deploy complete! Claude configuration updated for this machine"
echo ""
echo "📋 What was deployed:"
echo "  - Configuration files with paths adjusted to: $HOME"
echo "  - Hook scripts with executable permissions"
echo "  - Statusline script with executable permissions"
echo ""
echo "🔄 Next steps:"
echo "  1. Restart Claude Code to apply the new configuration"
echo "  2. Verify hooks and statusline are working correctly"
echo "  3. Use ./sync-from-claude.sh to capture any local changes"