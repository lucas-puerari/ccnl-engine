"""Root conftest — shared pytest hooks for the whole test suite."""

from __future__ import annotations

from typing import TYPE_CHECKING

from hypothesis import HealthCheck, settings

from tests.reference.provenance import CASES_DIR, count_by_status, load_case

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
    """Append reference-case counts per ``verification`` status."""
    del exitstatus, config  # required by pytest hook API, not used here
    cases = [load_case(path) for path in sorted(CASES_DIR.glob("*.json"))]
    total = len(cases)
    counts = count_by_status(cases)
    terminalreporter.write_sep(
        "-",
        "reference cases: "
        + " | ".join(f"{n}/{total} {status}" for status, n in counts.items()),
    )
