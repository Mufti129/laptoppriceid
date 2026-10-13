"""
Entry point wrapper for Streamlit Community Cloud deployment.
Executes the main LaptopPrice ID application logic on every rerun.
"""
import os
import sys
from pathlib import Path
import runpy

# Ensure root directory is on sys.path
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

_app_path = _ROOT / "app.py"
runpy.run_path(str(_app_path), run_name="__main__")
