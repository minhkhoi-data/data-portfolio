"""Bound the complete build, including Python validation, to 5 minutes."""
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
try:
    result=subprocess.run([sys.executable,'-u',str(ROOT/'scripts/run_project.py')],cwd=ROOT,timeout=300)
    raise SystemExit(result.returncode)
except subprocess.TimeoutExpired:
    raise SystemExit('Stopped after 300 seconds. Previous published outputs remain available; inspect audit/run.json and retry only after diagnosing.')
