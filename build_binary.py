#!/usr/bin/env python3
"""
Build standalone binary using PyInstaller.

This script creates a single executable file for audio-transcriber
that can be distributed without requiring Python installation.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path


def get_platform_name():
    """Get platform-specific naming."""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    return system


def build_binary():
    """Build the binary using PyInstaller."""
    print("[BUILD] Building audio-transcriber binary...")
    print(f"Platform: {platform.system()} {platform.machine()}")
    
    # Ensure PyInstaller is installed
    try:
        import PyInstaller
        print(f"[OK] PyInstaller {PyInstaller.__version__} found")
    except ImportError:
        print("[INFO] PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Get version from package
    import audio_transcriber
    version = audio_transcriber.__version__
    print(f"[INFO] Version: {version}")
    
    # PyInstaller options
    name = "audio-transcriber"
    
    options = [
        "src/audio_transcriber/__main__.py",  # Entry point
        f"--name={name}",
        "--onefile",  # Single executable
        "--console",  # Console application
        "--clean",  # Clean PyInstaller cache
        # Add hidden imports if needed
        "--hidden-import=audio_transcriber",
        "--hidden-import=audio_transcriber.cli",
        "--hidden-import=pydub",
        "--hidden-import=openai",
        "--hidden-import=tqdm",
        # Exclude unnecessary modules
        "--exclude-module=pytest",
        "--exclude-module=setuptools",
        "--exclude-module=pip",
        # Strip binary (smaller size)
        "--strip" if platform.system() != "Windows" else "",
    ]
    
    # Remove empty strings
    options = [opt for opt in options if opt]
    
    print("[BUILD] Running PyInstaller with options:")
    for opt in options:
        print(f"   {opt}")
    
    # Run PyInstaller
    try:
        subprocess.check_call(["pyinstaller"] + options)
        print("\n[SUCCESS] Build successful!")
        
        # Show binary location
        binary_path = Path("dist") / name
        if platform.system() == "Windows":
            binary_path = binary_path.with_suffix(".exe")
        
        if binary_path.exists():
            size_mb = binary_path.stat().st_size / (1024 * 1024)
            print(f"\n[INFO] Binary location: {binary_path}")
            print(f"[INFO] Binary size: {size_mb:.2f} MB")
            print(f"\n[SUCCESS] You can now distribute: {binary_path.absolute()}")
            
            # Test binary
            print("\n[TEST] Testing binary...")
            result = subprocess.run(
                [str(binary_path.absolute()), "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"[OK] Binary test passed: {result.stdout.strip()}")
            else:
                print(f"[WARNING] Binary test failed: {result.stderr}")
        else:
            print(f"[ERROR] Binary not found at: {binary_path}")
            return 1
            
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Build failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(build_binary())
