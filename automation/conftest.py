import sys
from pathlib import Path

# Makes `app` importable as a top-level package when running pytest from
# this directory, regardless of pytest version/rootdir detection.
sys.path.insert(0, str(Path(__file__).parent))
