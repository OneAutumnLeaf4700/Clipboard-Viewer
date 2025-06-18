#!/usr/bin/env python
"""
Clipboard Viewer - A PyQt6-based clipboard history manager

This is the main entry point for the application.
"""

import os
import sys

# Add the src directory to the Python path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_dir)

# Import the main module
from main import main

if __name__ == "__main__":
    main()