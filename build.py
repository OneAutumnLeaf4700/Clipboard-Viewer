#!/usr/bin/env python3
"""
Build script for Clipboard Viewer
Creates a Windows executable using PyInstaller with optimized settings.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build_dirs():
    """Clean previous build directories."""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name}...")
            shutil.rmtree(dir_name)
    
    # Clean .spec files
    for spec_file in Path('.').glob('*.spec'):
        print(f"Removing {spec_file}...")
        spec_file.unlink()

def create_spec_file():
    """Create PyInstaller spec file with optimized settings."""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Get the current directory
current_dir = Path(__file__).parent

# Define data files to include
datas = [
    ('assets', 'assets'),
    ('src/gui/themes', 'gui/themes'),
    ('src/utils', 'utils'),
]

# Define hidden imports
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'win32clipboard',
    'win32api',
    'win32con',
    'PIL',
    'PIL.Image',
    'PIL.ImageGrab',
    'keyboard',
    'pynput',
    'sqlite3',
    'hashlib',
    'json',
    'pickle',
    'datetime',
    'threading',
    'logging',
    'os',
    'sys',
    'time',
]

# Define excluded modules to reduce size
excludes = [
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'tkinter',
    'PyQt5',
    'PySide2',
    'PySide6',
    'IPython',
    'jupyter',
    'notebook',
    'sphinx',
    'pytest',
    'unittest',
    'doctest',
    'pdb',
    'pydoc',
]

a = Analysis(
    ['src/main.py'],
    pathex=[str(current_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ClipboardViewer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/app_icon.ico' if Path('assets/icons/app_icon.ico').exists() else None,
    version_file=None,
)
'''
    
    with open('clipboard_viewer.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("Created clipboard_viewer.spec")

def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    
    # Install PyInstaller if not already installed
    try:
        import PyInstaller
        print("PyInstaller is already installed")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'PyInstaller'])
    
    # Install other dependencies
    dependencies = [
        'PyQt6>=6.0.0',
        'pyperclip>=1.8.2',
        'pynput>=1.7.6',
        'pillow>=9.0.0',
        'keyboard>=0.13.5',
        'pywin32>=303',
    ]
    
    for dep in dependencies:
        print(f"Installing {dep}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])

def build_executable():
    """Build the executable using PyInstaller."""
    print("Building executable...")
    
    # Build with spec file
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        'clipboard_viewer.spec'
    ]
    
    try:
        subprocess.check_call(cmd)
        print("Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        return False

def create_installer_script():
    """Create a simple installer script."""
    installer_content = '''@echo off
echo Installing Clipboard Viewer...

REM Create installation directory
set INSTALL_DIR=%LOCALAPPDATA%\\ClipboardViewer
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy executable
copy "dist\\ClipboardViewer.exe" "%INSTALL_DIR%\\"

REM Create desktop shortcut
set DESKTOP=%USERPROFILE%\\Desktop
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%DESKTOP%\\Clipboard Viewer.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%INSTALL_DIR%\\ClipboardViewer.exe" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> CreateShortcut.vbs
echo oLink.Description = "Clipboard Viewer - Advanced clipboard history manager" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript CreateShortcut.vbs
del CreateShortcut.vbs

REM Add to startup (optional)
set /p ADD_STARTUP="Add to Windows startup? (y/n): "
if /i "%ADD_STARTUP%"=="y" (
    reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "ClipboardViewer" /t REG_SZ /d "%INSTALL_DIR%\\ClipboardViewer.exe" /f
    echo Added to Windows startup.
)

echo Installation completed!
echo Clipboard Viewer has been installed to: %INSTALL_DIR%
pause
'''
    
    with open('install.bat', 'w', encoding='utf-8') as f:
        f.write(installer_content)
    
    print("Created install.bat")

def create_uninstaller_script():
    """Create an uninstaller script."""
    uninstaller_content = '''@echo off
echo Uninstalling Clipboard Viewer...

REM Remove from startup
reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "ClipboardViewer" /f 2>nul

REM Remove desktop shortcut
del "%USERPROFILE%\\Desktop\\Clipboard Viewer.lnk" 2>nul

REM Remove installation directory
set INSTALL_DIR=%LOCALAPPDATA%\\ClipboardViewer
if exist "%INSTALL_DIR%" (
    rmdir /s /q "%INSTALL_DIR%"
    echo Removed installation directory: %INSTALL_DIR%
)

echo Uninstallation completed!
pause
'''
    
    with open('uninstall.bat', 'w', encoding='utf-8') as f:
        f.write(uninstaller_content)
    
    print("Created uninstall.bat")

def create_readme():
    """Create a README for the build."""
    readme_content = '''# Clipboard Viewer - Build Instructions

## Building the Executable

1. Install Python 3.8 or higher
2. Run the build script:
   ```
   python build.py
   ```

## Installation

1. Run `install.bat` as administrator
2. Follow the prompts to install the application
3. A desktop shortcut will be created

## Uninstallation

1. Run `uninstall.bat` as administrator
2. This will remove the application and all shortcuts

## Manual Installation

1. Copy `ClipboardViewer.exe` to your desired location
2. Run the executable directly

## Requirements

- Windows 10 or higher
- No additional dependencies required (all included in executable)

## Features

- Real-time clipboard monitoring
- Persistent history storage
- Advanced search and filtering
- System tray integration
- Customizable hotkeys
- Multiple theme support
- Export functionality
- Cross-platform UI

## Troubleshooting

If the application doesn't start:
1. Check Windows Defender/antivirus settings
2. Run as administrator
3. Check Windows Event Viewer for error details

## Support

For issues and feature requests, please visit the project repository.
'''
    
    with open('BUILD_README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("Created BUILD_README.md")

def main():
    """Main build function."""
    print("Clipboard Viewer Build Script")
    print("=" * 40)
    
    # Check if we're on Windows
    if sys.platform != 'win32':
        print("Warning: This build script is optimized for Windows.")
        print("The application may work on other platforms but is not tested.")
    
    # Clean previous builds
    clean_build_dirs()
    
    # Install dependencies
    install_dependencies()
    
    # Create spec file
    create_spec_file()
    
    # Build executable
    if build_executable():
        print("\\nBuild completed successfully!")
        print("Executable location: dist/ClipboardViewer.exe")
        
        # Create installer scripts
        create_installer_script()
        create_uninstaller_script()
        create_readme()
        
        print("\\nAdditional files created:")
        print("- install.bat (Windows installer)")
        print("- uninstall.bat (Windows uninstaller)")
        print("- BUILD_README.md (Build documentation)")
        
        # Show file size
        exe_path = Path('dist/ClipboardViewer.exe')
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\\nExecutable size: {size_mb:.1f} MB")
        
    else:
        print("\\nBuild failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
