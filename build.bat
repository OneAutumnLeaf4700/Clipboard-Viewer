@echo off
echo Building Clipboard Viewer...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Run the build script
python build.py

REM Check if build was successful
if exist "dist\ClipboardViewer.exe" (
    echo.
    echo Build completed successfully!
    echo Executable: dist\ClipboardViewer.exe
    echo.
    set /p OPEN_FOLDER="Open dist folder? (y/n): "
    if /i "%OPEN_FOLDER%"=="y" (
        explorer dist
    )
) else (
    echo.
    echo Build failed!
    echo Check the output above for errors.
)

pause
