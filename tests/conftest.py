"""Root conftest — shared pytest hooks for the whole test suite."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest


def pytest_terminal_summary(
    terminalreporter: pytest.TerminalReporter,
    exitstatus: int,
    config: pytest.Config,
) -> None:
    """Append a one-line reference-coverage count at the end of the session.

    Counts how many case files in ``tests/reference/cases/`` carry a
    machine-readable ``source`` block (i.e. have been traced back to a
    primary document such as a payslip or official salary table).
    """
    del exitstatus, config  # required by pytest hook API, not used here
    cases_dir = Path(__file__).parent / "reference" / "cases"
    if not cases_dir.is_dir():
        return
    total = 0
    verified = 0
    for path in cases_dir.glob("*.json"):
        total += 1
        case = json.loads(path.read_text(encoding="utf-8"))
        if case.get("source"):
            verified += 1
    terminalreporter.write_sep("-", f"reference cases: {verified}/{total} with source")
