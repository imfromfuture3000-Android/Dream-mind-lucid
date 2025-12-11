#!/usr/bin/env python3
"""
Test for the install command functionality
-----------------------------------------
"""

import subprocess
import sys
import os

def test_install_command_exists():
    """Test that the install command is available in grok_copilot_launcher."""
    result = subprocess.run([
        sys.executable, "grok_copilot_launcher.py", "invalid_command"
    ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
    
    # Should show help with install command listed (output goes to stdout)
    output = result.stdout + result.stderr
    assert "install" in output, f"Install command not found in help: {output}"
    assert result.returncode == 1, "Should return error code for invalid command"
    print("✅ Install command is listed in help")

def test_install_command_runs():
    """Test that the install command runs without crashing."""
    # Run install command (might fail due to permissions but shouldn't crash)
    result = subprocess.run([
        sys.executable, "grok_copilot_launcher.py", "install"
    ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
    
    # Should mention installation attempt
    assert "Installing Dream-Mind-Lucid dependencies" in result.stdout, f"Expected install message not found: {result.stdout}"
    print("✅ Install command runs and shows installation message")

def test_launcher_status():
    """Test that the launcher status shows correctly after install."""
    result = subprocess.run([
        sys.executable, "grok_copilot_launcher.py"
    ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
    
    # Should show status
    assert "Grok Copilot Launcher Ready" in result.stdout, f"Status not shown: {result.stdout}"
    assert result.returncode == 0, "Status should return success"
    print("✅ Launcher status works correctly")

if __name__ == "__main__":
    print("🧪 Testing install command functionality...")
    test_install_command_exists()
    test_install_command_runs()
    test_launcher_status()
    print("✅ All tests passed!")