"""
Root conftest.py — ensures the build/ directory is on sys.path so that
`from backend.xxx import ...` works in tests without installing the package.
"""
import sys
from pathlib import Path

# Add build/ root to sys.path so `import backend` resolves correctly
sys.path.insert(0, str(Path(__file__).parent))
