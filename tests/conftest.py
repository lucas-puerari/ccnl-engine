"""Root conftest — shared pytest hooks for the whole test suite."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from hypothesis import HealthCheck, settings

if TYPE_CHECKING:
    import pytest

settings.register_profile(
    "ci",
    deadline=None,
    derandomize=True,
    max_examples=60,
    suppress_health_check=[HealthCheck.too_slow],
)
settings.load_profile("ci")


def pytest_terminal_summary(
    terminalreporter: pytest.TerminalReporter,
    exitstatus: int,
    config: pytest.Config,
) -> None:
    """Append reference-case provenance counts at the end of the session.

    Three buckets:
    - ``verified``: ``source.verification_status == 'verified'``
    - ``source_present``: has a ``source`` block but not yet ``verified``
    - ``engine_generated``: no ``source`` block at all
    """
    del exitstatus, config  # required by pytest hook API, not used here
    cases_dir = Path(__file__).parent / "reference" / "cases"
    if not cases_dir.is_dir():
        return
    total = 0
    verified = 0
    source_present = 0
    for path in cases_dir.glob("*.json"):
        total += 1
        case = json.loads(path.read_text(encoding="utf-8"))
        src = case.get("source")
        if isinstance(src, dict) and src.get("verification_status") == "verified":
            verified += 1
        elif src:
            source_present += 1
    engine_generated = total - verified - source_present
    terminalreporter.write_sep(
        "-",
        f"reference cases: {verified}/{total} verified"
        f" | {source_present}/{total} source-linked"
        f" | {engine_generated}/{total} engine-generated",
    )
