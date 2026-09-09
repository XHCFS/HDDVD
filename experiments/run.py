#!/usr/bin/env python3
"""Run every experiment in this directory. Exit non-zero on first failure."""
import subprocess
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
scripts = sorted(here.glob("e*.py"))
assert scripts
for s in scripts:
    print("=" * 60, s.name)
    r = subprocess.run([sys.executable, str(s)], cwd=here)
    if r.returncode != 0:
        sys.exit(r.returncode)
print("ALL EXPERIMENTS PASS")
