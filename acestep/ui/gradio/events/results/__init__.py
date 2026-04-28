"""
Results sub-package.

Focused modules for result handling, scoring, batch management, LRC utilities,
audio transfer, and generation progress.
"""

# Add this directory to sys.path so test support modules can be imported
# by test files using plain (non-relative) imports.
import os
import sys

_results_dir = os.path.dirname(os.path.abspath(__file__))
if _results_dir not in sys.path:
    sys.path.insert(0, _results_dir)
