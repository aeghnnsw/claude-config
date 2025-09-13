#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///

import json
import sys
import re
from pathlib import Path

def is_dangerous_rm_command(command):
    """
    Selective detection of dangerous rm commands.
    Only blocks rm commands with dangerous paths or patterns while allowing explicit removals.
    """
    # Normalize command by removing extra spaces and converting to lowercase
    normalized = ' '.join(command.lower().split())
    
    # Allow specific safe patterns for explicit removals
    safe_explicit_patterns = [
        r'\brm\s+-rf\s+(["\']?[/a-zA-Z_][a-zA-Z0-9_./-]*["\']?\s*)+$',  # rm -rf specific files/folders
        r'\brm\s+-r\s+(["\']?[/a-zA-Z_][a-zA-Z0-9_./-]*["\']?\s*)+$',   # rm -r specific files/folders  
        r'\brm\s+-f\s+(["\']?[/a-zA-Z_][a-zA-Z0-9_./-]*["\']?\s*)+$',   # rm -f specific files
        r'\brm\s+(["\']?[/a-zA-Z_][a-zA-Z0-9_./-]*["\']?\s*)+$',        # rm specific files/folders
    ]
    
    # Check if command matches safe explicit patterns
    for pattern in safe_explicit_patterns:
        if re.search(pattern, command):  # Use original case-sensitive command
            return False
    
    # Dangerous path patterns that should always be blocked
    dangerous_paths = [
        r'/',           # Root directory
        r'/\*',         # Root with wildcard
        r'~/?$',        # Home directory (exact match)
        r'~/',          # Home directory path
        r'\$HOME',      # Home environment variable
        r'\.\.',        # Parent directory references
        r'\*',          # Wildcards
        r'\s\.\s*$',    # Current directory (space dot space/end)
        r'^\s*\.\s*$',  # Just current directory
        r'/usr',        # System directories
        r'/var',
        r'/etc',
        r'/bin',
        r'/sbin',
        r'/lib',
        r'/opt',
    ]
    
    # Block any rm command (with or without flags) that targets dangerous paths
    if re.search(r'\brm\s+', normalized):
        for path in dangerous_paths:
            if re.search(path, normalized):
                return True
    
    return False

def is_env_file_access(tool_name, tool_input):
    """
    Check if any tool is trying to access .env files containing sensitive data.
    """
    if tool_name in ['Read', 'Edit', 'MultiEdit', 'Write', 'Bash']:
        # Check file paths for file-based tools
        if tool_name in ['Read', 'Edit', 'MultiEdit', 'Write']:
            file_path = tool_input.get('file_path', '')
            if '.env' in file_path and not file_path.endswith('.env.sample'):
                return True
        
        # Check bash commands for .env file access
        elif tool_name == 'Bash':
            command = tool_input.get('command', '')
            # Pattern to detect .env file access (but allow .env.sample)
            env_patterns = [
                r'\b\.env\b(?!\.sample)',  # .env but not .env.sample
                r'cat\s+.*\.env\b(?!\.sample)',  # cat .env
                r'echo\s+.*>\s*\.env\b(?!\.sample)',  # echo > .env
                r'touch\s+.*\.env\b(?!\.sample)',  # touch .env
                r'cp\s+.*\.env\b(?!\.sample)',  # cp .env
                r'mv\s+.*\.env\b(?!\.sample)',  # mv .env
            ]
            
            for pattern in env_patterns:
                if re.search(pattern, command):
                    return True
    
    return False

def main():
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)
        
        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})
        
        # Check for .env file access (blocks access to sensitive environment files)
        if is_env_file_access(tool_name, tool_input):
            print("BLOCKED: Access to .env files containing sensitive data is prohibited", file=sys.stderr)
            print("Use .env.sample for template files instead", file=sys.stderr)
            sys.exit(2)  # Exit code 2 blocks tool call and shows error to Claude
        
        # Check for dangerous rm -rf commands
        if tool_name == 'Bash':
            command = tool_input.get('command', '')
            
            # Block dangerous rm commands while allowing explicit removals
            if is_dangerous_rm_command(command):
                print("BLOCKED: Potentially dangerous rm command detected", file=sys.stderr)
                print("Safe explicit removals like 'rm -rf specific_folder' are allowed", file=sys.stderr)
                sys.exit(2)  # Exit code 2 blocks tool call and shows error to Claude
        
        # Ensure log directory exists
        log_dir = Path.cwd() / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / 'pre_tool_use.json'
        
        # Read existing log data or initialize empty list
        if log_path.exists():
            with open(log_path, 'r') as f:
                try:
                    log_data = json.load(f)
                except (json.JSONDecodeError, ValueError):
                    log_data = []
        else:
            log_data = []
        
        # Append new data
        log_data.append(input_data)
        
        # Write back to file with formatting
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        sys.exit(0)
        
    except json.JSONDecodeError:
        # Gracefully handle JSON decode errors
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)

if __name__ == '__main__':
    main()