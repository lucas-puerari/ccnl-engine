"""The path filters of the workflows name directories that exist.

A filter on a directory that was renamed never triggers its workflow, so
the check it runs goes stale without failing.
"""

from __future__ import annotations

import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
_PATH = re.compile(r'^\s+- "([^"*]+?)(?:/\*\*)?"\s*$', re.MULTILINE)


def test_every_path_filter_names_something_that_exists() -> None:
    """Each literal prefix of a ``paths:`` filter is a file or a directory."""
    missing = [
        f"{workflow.name}: {prefix}"
        for workflow in sorted((_ROOT / ".github" / "workflows").glob("*.yml"))
        for prefix in _PATH.findall(workflow.read_text(encoding="utf-8"))
        if "/" in prefix and not (_ROOT / prefix).exists()
    ]
    assert missing == []
