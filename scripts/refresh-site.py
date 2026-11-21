#!/usr/bin/env python3
"""Refresh generated public navigation and indexes in dependency order."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
for command in [
    [sys.executable, 'scripts/build-public-resources.py'],
    ['node', 'scripts/build-site-chrome.mjs'],
    [sys.executable, 'scripts/build-sitemap.py'],
    [sys.executable, 'scripts/build-guide.py', '--local-site', '.'],
    [sys.executable, 'scripts/build-search.py'],
    [sys.executable, 'scripts/check-site.py'],
]:
    subprocess.run(command, cwd=ROOT, check=True)
