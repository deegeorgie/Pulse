# run.py
import sys
import os

# Add the parent directory of 'pulse' to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Now launch the app
import pulse.main