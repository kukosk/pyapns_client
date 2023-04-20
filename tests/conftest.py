import os
import sys

# Get the path to the parent directory of the tests directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add the parent directory to the Python path
sys.path.insert(0, parent_dir)
