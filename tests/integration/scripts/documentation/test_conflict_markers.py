"""No committed text file keeps the markers of a merge conflict.

A generated page merged with a conflict and regenerated keeps its counts
right while the markers stay: the docs build and the count checks pass on
it. This test fails on any tracked Markdown, JSON or Python file with a line
that opens or closes a conflict.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

_ROOT = Path(__file__).parents[4]
_MARKERS = ("<<<<<<< ", ">>>>>>> ")


def test_no_tracked_file_keeps_conflict_markers() -> None:
    """Every line starting a conflict side is a leftover of a bad merge."""
    tracked = subprocess.run(
        ["git", "ls-files", "*.md", "*.json", "*.py"],
        cwd=_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.split()
    marked = [
        name
        for name in tracked
        if any(
            line.startswith(_MARKERS)
            for line in (_ROOT / name).read_text(encoding="utf-8").splitlines()
        )
    ]

    assert marked == []
