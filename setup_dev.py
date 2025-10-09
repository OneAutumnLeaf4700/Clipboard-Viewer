#!/usr/bin/env python3
"""
Development setup script for Clipboard Viewer
Sets up the development environment with all required dependencies.
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    return True

def install_dependencies():
    """Install development dependencies."""
    print("Installing development dependencies...")
    
    # Install requirements
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    
    # Install development tools
    dev_tools = [
        'pytest>=7.0.0',
        'pytest-qt>=4.2.0',
        'black>=22.0.0',
        'flake8>=5.0.0',
        'mypy>=0.991',
    ]
    
    for tool in dev_tools:
        print(f"Installing {tool}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', tool])

def create_data_directory():
    """Create data directory for development."""
    data_dir = Path('data')
    if not data_dir.exists():
        data_dir.mkdir()
        print("Created data directory")

def setup_git_hooks():
    """Setup git hooks for development."""
    hooks_dir = Path('.git/hooks')
    if hooks_dir.exists():
        # Create pre-commit hook
        pre_commit_hook = hooks_dir / 'pre-commit'
        pre_commit_content = '''#!/bin/sh
# Run code formatting
python -m black src/ --check
if [ $? -ne 0 ]; then
    echo "Code formatting check failed. Run 'python -m black src/' to fix."
    exit 1
fi

# Run linting
python -m flake8 src/
if [ $? -ne 0 ]; then
    echo "Linting failed. Fix the issues above."
    exit 1
fi
'''
        with open(pre_commit_hook, 'w') as f:
            f.write(pre_commit_content)
        
        # Make executable on Unix systems
        if platform.system() != 'Windows':
            os.chmod(pre_commit_hook, 0o755)
        
        print("Created git pre-commit hook")

def create_launch_config():
    """Create VS Code launch configuration."""
    vscode_dir = Path('.vscode')
    if not vscode_dir.exists():
        vscode_dir.mkdir()
    
    launch_config = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Run Clipboard Viewer",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/src/main.py",
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}",
                "env": {
                    "PYTHONPATH": "${workspaceFolder}/src"
                }
            },
            {
                "name": "Debug Clipboard Viewer",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/src/main.py",
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}",
                "env": {
                    "PYTHONPATH": "${workspaceFolder}/src"
                },
                "justMyCode": False
            }
        ]
    }
    
    import json
    with open(vscode_dir / 'launch.json', 'w') as f:
        json.dump(launch_config, f, indent=4)
    
    print("Created VS Code launch configuration")

def main():
    """Main setup function."""
    print("Clipboard Viewer Development Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    install_dependencies()
    
    # Create data directory
    create_data_directory()
    
    # Setup git hooks
    setup_git_hooks()
    
    # Create VS Code config
    create_launch_config()
    
    print("\nDevelopment environment setup completed!")
    print("\nNext steps:")
    print("1. Run the application: python src/main.py")
    print("2. Run tests: python -m pytest")
    print("3. Format code: python -m black src/")
    print("4. Lint code: python -m flake8 src/")

if __name__ == '__main__':
    from pathlib import Path
    main()
