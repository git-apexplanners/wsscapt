"""Script to create the application icon."""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the icon creation module
from slot_analyzer.ui.assets.create_icon import create_icon

if __name__ == "__main__":
    print("Creating application icon...")
    create_icon()
    print("Done!")
