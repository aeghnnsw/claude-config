#!/bin/bash

# Sync script: ~/.claude → templates
# Extracts current Claude configuration and converts to templates

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
TEMPLATES_DIR="$SCRIPT_DIR/templates"

echo "🔄 Syncing configuration from ~/.claude to templates..."

# Check if ~/.claude exists
if [[ ! -d "$CLAUDE_DIR" ]]; then
    echo "❌ Error: ~/.claude directory not found"
    exit 1
fi

# Create templates directory structure
mkdir -p "$TEMPLATES_DIR/hooks"

# Function to convert paths to template placeholders
convert_to_template() {
    local file="$1"
    local output="$2"

    # Replace current user's home directory with {{HOME}} placeholder
    sed "s|$HOME|{{HOME}}|g" "$file" > "$output"
}

# Sync settings.json if it exists
if [[ -f "$CLAUDE_DIR/settings.json" ]]; then
    echo "📄 Syncing settings.json..."
    convert_to_template "$CLAUDE_DIR/settings.json" "$TEMPLATES_DIR/settings.json"
else
    echo "⚠️  Warning: settings.json not found in ~/.claude"
fi

# Sync statusline script if it exists
if [[ -f "$CLAUDE_DIR/statusline-with-tokens.sh" ]]; then
    echo "📄 Syncing statusline-with-tokens.sh..."
    cp "$CLAUDE_DIR/statusline-with-tokens.sh" "$TEMPLATES_DIR/statusline-with-tokens.sh"
else
    echo "⚠️  Warning: statusline-with-tokens.sh not found in ~/.claude"
fi

# Sync hook files
if [[ -d "$CLAUDE_DIR/hooks" ]]; then
    echo "📄 Syncing hook files..."
    for hook_file in "$CLAUDE_DIR/hooks"/*.py; do
        if [[ -f "$hook_file" ]]; then
            filename=$(basename "$hook_file")
            echo "  - $filename"
            convert_to_template "$hook_file" "$TEMPLATES_DIR/hooks/$filename"
        fi
    done

else
    echo "⚠️  Warning: hooks directory not found in ~/.claude"
fi

echo "✅ Sync complete! Templates updated with current ~/.claude configuration"
echo ""
echo "📋 Next steps:"
echo "  1. Review the changes in templates/"
echo "  2. Commit changes if desired: git add . && git commit -m 'Update templates'"
echo "  3. Use deploy.sh to apply templates to other machines"