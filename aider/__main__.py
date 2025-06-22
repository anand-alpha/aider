import sys
import os

# Add the parent directory to sys.path to enable absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aider.main import main

if __name__ == "__main__":
    main()
