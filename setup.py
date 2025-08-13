#!/usr/bin/env python3
"""
Setup script for the Timer API application.
This script initializes required directories and sample sound files.
"""

import os
import json
from pathlib import Path

def create_directories():
    """Create required directories"""
    dirs = [
        "sounds",
        "custom_sounds",
        "logs"
    ]
    
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"Created directory: {dir_name}")

def create_sample_sound_files():
    """Create placeholder sound files for testing"""
    sounds_dir = Path("sounds")
    sound_files = [
        "chime.wav",
        "bell.wav", 
        "beep.wav",
        "nature.wav",
        "digital.wav"
    ]
    
    for sound_file in sound_files:
        file_path = sounds_dir / sound_file
        if not file_path.exists():
            # Create a small placeholder file
            with open(file_path, 'wb') as f:
                # Write a minimal WAV header for testing
                f.write(b'RIFF$\x00\x00\x00WAVE')
            print(f"Created placeholder sound file: {sound_file}")

def create_config_files():
    """Create configuration files if they don't exist"""
    # Create empty timers.json if it doesn't exist
    if not Path("timers.json").exists():
        with open("timers.json", 'w') as f:
            json.dump({}, f)
        print("Created timers.json")
    
    # Create empty users.json if it doesn't exist
    if not Path("users.json").exists():
        with open("users.json", 'w') as f:
            json.dump({}, f)
        print("Created users.json")

def main():
    """Main setup function"""
    print("Setting up Timer API application...")
    
    create_directories()
    create_sample_sound_files()
    create_config_files()
    
    print("\nSetup completed successfully!")
    print("\nTo run the application:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run setup: python setup.py")
    print("3. Start server: python main.py")
    print("4. Run tests: pytest test_timers.py -v")

if __name__ == "__main__":
    main()