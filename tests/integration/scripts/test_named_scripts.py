"""Every script the package or its configuration names exists."""

from __future__ import annotations

import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
_SCRIPT = re.compile(r"\b(?:scripts/[\w/]+\.py|[\w]+_build\.py)\b")


def test_named_scripts_exist() -> None:
    """A remediation or a comment never points at a script that is gone."""
    texts = [*sorted((_ROOT / "src").rglob("*.py")), _ROOT / "pyproject.toml"]
    missing = sorted({
        f"{path.relative_to(_ROOT)}: {name}"
        for path in texts
        for name in _SCRIPT.findall(path.read_text(encoding="utf-8"))
        if not (_ROOT / name).exists()
    })
    assert missing == []
