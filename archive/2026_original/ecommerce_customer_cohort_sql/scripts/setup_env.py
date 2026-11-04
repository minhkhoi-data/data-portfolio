"""Create an isolated environment; install only the pinned DuckDB wheel."""
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
if sys.version_info < (3,10):
    raise SystemExit('Python 3.10 or newer is required. Use an Anaconda Prompt with a supported Python.')
env=ROOT/'.venv'
python=env/('Scripts/python.exe' if sys.platform=='win32' else 'bin/python')
if not python.exists():
    subprocess.run([sys.executable,'-m','venv',str(env)],check=True,timeout=90)
subprocess.run([str(python),'-m','pip','install','--disable-pip-version-check',
    '--only-binary=:all:','--timeout','15','--retries','1','-r',str(ROOT/'requirements.txt')],
    check=True,timeout=180)
print('Environment ready. Run RUN_SQL.cmd on Windows, or .venv/bin/python scripts/run_project.py elsewhere.')
