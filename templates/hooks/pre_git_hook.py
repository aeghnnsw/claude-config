#!/usr/bin/env python3
"""
Claude Code hook for git operations.
Adds context reminders before git commits and PR creation.
"""

import json
import sys

def main():
    # Read input from stdin
    try:
        input_data = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        print("Error: Invalid JSON input", file=sys.stderr)
        sys.exit(1)
    
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    
    # Check if this is a git operation
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        if "git add ." in command:
            # Allow git add for specific dotfiles, but block git add .
            import re
            # Check if it's adding a specific dotfile (like .gitignore, .env.example, etc.)
            dotfile_pattern = r'git add \.[a-zA-Z][a-zA-Z0-9._-]*'
            if not re.search(dotfile_pattern, command) or command.strip() == "git add .":
                # Block git add . operations
                response = {
                    "systemMessage": "❌ BLOCKED: Use 'git add <filename>' with specific file names instead of 'git add .' for precise change control.",
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": "git add . is prohibited - use specific file names"
                    }
                }
                print(json.dumps(response))
                sys.exit(0)
        elif "git checkout -b" in command or "git switch -c" in command:
            # Extract branch name and validate naming convention
            import re
            
            # Extract branch name from command
            if "git checkout -b" in command:
                match = re.search(r'git checkout -b\s+(\S+)', command)
            else:  # git switch -c
                match = re.search(r'git switch -c\s+(\S+)', command)
            
            if match:
                branch_name = match.group(1)
                valid_prefixes = ['feat-', 'bugfix-', 'doc-', 'refactor-', 'chore-', 'test-']
                
                if not any(branch_name.startswith(prefix) for prefix in valid_prefixes):
                    # Block invalid branch name
                    response = {
                        "systemMessage": f"Branch name '{branch_name}' is invalid. Use only these prefixes: feat-, bugfix-, doc-, refactor-, chore-, test-",
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "permissionDecision": "deny",
                            "permissionDecisionReason": f"Branch name must start with one of: {', '.join(valid_prefixes)}"
                        }
                    }
                    print(json.dumps(response))
                    sys.exit(0)
            
            # Valid branch name, just show reminder
            response = {
                "systemMessage": "Branch Naming Convention: Using approved prefix - good practice!"
            }
            print(json.dumps(response))
            sys.exit(0)
        elif "gh pr merge" in command and "--squash" in command:
            # Warn about squash merge
            response = {
                "systemMessage": "Merge Strategy: Use regular merge instead of squash to preserve commit history and authorship."
            }
            print(json.dumps(response))
            sys.exit(0)
        elif "git commit" in command or "gh pr create" in command:
            # Check for Claude Code attribution patterns
            import re
            claude_patterns = [
                r'Generated with \[Claude Code\]',
                r'claude\.ai/code',
                r'Co-Authored-By: Claude <noreply@anthropic\.com>',
                r'🤖 Generated with',
                r'Claude Code'
            ]
            
            # Check the command content for Claude attribution
            for pattern in claude_patterns:
                if re.search(pattern, command, re.IGNORECASE):
                    # Block the operation
                    response = {
                        "systemMessage": "❌ BLOCKED: Git operation contains Claude Code attribution. Remove AI contribution messages from commit messages and PR descriptions.",
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "permissionDecision": "deny",
                            "permissionDecisionReason": "Claude Code attribution detected in git operation"
                        }
                    }
                    print(json.dumps(response))
                    sys.exit(0)
            
            # Output JSON with systemMessage to show reminder to user
            response = {
                "systemMessage": "Commit Guidelines: Keep messages concise and accurate. Avoid AI attribution in commit messages or PR descriptions."
            }
            print(json.dumps(response))
            sys.exit(0)
            
    # Allow the operation to continue (no git operation detected)
    sys.exit(0)

if __name__ == "__main__":
    main()