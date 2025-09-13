#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///

import json
import sys
import subprocess
import platform
from pathlib import Path

def play_system_sound(sound_type="default"):
    """
    Play system notification sound based on the operating system.
    
    Args:
        sound_type: Type of sound to play ("success", "attention", "default")
    """
    try:
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            # macOS system sounds
            sound_map = {
                "success": "Glass",
                "attention": "Sosumi", 
                "default": "Ping",
                "error": "Basso"
            }
            sound_name = sound_map.get(sound_type, "Ping")
            subprocess.run(["afplay", f"/System/Library/Sounds/{sound_name}.aiff"], 
                         capture_output=True, timeout=5)
            
        elif system == "linux":
            # Linux - try different approaches
            sound_map = {
                "success": "complete",
                "attention": "bell", 
                "default": "bell",
                "error": "error"
            }
            sound_name = sound_map.get(sound_type, "bell")
            
            # Try paplay first (PulseAudio)
            try:
                subprocess.run(["paplay", f"/usr/share/sounds/sound-icons/{sound_name}.wav"], 
                             capture_output=True, timeout=5, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to system beep
                subprocess.run(["printf", "\a"], capture_output=True, timeout=2)
                
        elif system == "windows":
            # Windows system sounds
            import winsound
            sound_map = {
                "success": winsound.MB_OK,
                "attention": winsound.MB_ICONEXCLAMATION,
                "default": winsound.MB_ICONASTERISK,
                "error": winsound.MB_ICONHAND
            }
            sound_type_code = sound_map.get(sound_type, winsound.MB_ICONASTERISK)
            winsound.MessageBeep(sound_type_code)
        else:
            # Fallback - terminal bell
            print("\a", end="", flush=True)
            
    except Exception:
        # Ultimate fallback - terminal bell
        try:
            print("\a", end="", flush=True)
        except:
            pass  # Silent failure


def main():
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)
        
        # Ensure log directory exists
        log_dir = Path.cwd() / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / 'system_notification.json'
        
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
        
        # Determine sound type based on hook event and context
        hook_event = input_data.get('hook_event_name', '')
        tool_name = input_data.get('tool_name', '')
        
        # Play different sounds for different events
        if hook_event == 'UserPromptSubmit':
            # Claude is waiting for user input
            play_system_sound("attention")
        elif hook_event == 'PostToolUse':
            # Tool execution completed
            if tool_name in ['Bash', 'Write', 'Edit', 'MultiEdit']:
                play_system_sound("success")
            else:
                play_system_sound("default")
        elif hook_event == 'Stop':
            # Session/task completion
            play_system_sound("success")
        else:
            # Default notification
            play_system_sound("default")
        
        sys.exit(0)
        
    except json.JSONDecodeError:
        # Gracefully handle JSON decode errors
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)

if __name__ == '__main__':
    main()