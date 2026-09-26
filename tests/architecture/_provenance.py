"""Verification status rules for reference case fixtures.

Every JSON file in ``tests/fixtures/expected/`` declares a top-level
``verification`` field stating how far its expected values can be trusted:

- ``verified``: expected values checked against an independent source (a real
  payslip or an official worked example), not produced by this engine.
- ``source_linked``: the case cites the primary source it models, but its
  expected values have not been independently checked.
- ``engine_generated``: expected values were produced by the engine itself and
  cite no source. Such a case only detects regressions, never systematic errors.

``verified`` and ``source_linked`` cases must carry a non-empty ``source``
object.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Final

CASES_DIR: Final = Path(__file__).parents[1] / "fixtures" / "expected"
VERIFICATION_STATUSES: Final = ("verified", "source_linked", "engine_generated")
_SOURCED_STATUSES: Final = frozenset({"verified", "source_linked"})


def load_case(path: Path) -> dict[str, object]:
    """Read one reference case JSON file.

    Returns:
        The decoded JSON object.

    Raises:
        TypeError: If the file does not contain a JSON object.
    """
    data: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        msg = f"{path.name}: reference case must be a JSON object"
        raise TypeError(msg)
    return data


def verification_errors(case: dict[str, object]) -> list[str]:
    """Return every provenance rule the case violates.

    Returns:
        Human-readable error messages; empty when the case is valid.
    """
    status = case.get("verification")
    if status is None:
        return ["missing 'verification' field"]
    if status not in VERIFICATION_STATUSES:
        allowed = list(VERIFICATION_STATUSES)
        return [f"unknown verification {status!r}; allowed: {allowed}"]
    source = case.get("source")
    if source is not None and not isinstance(source, dict):
        return [f"'source' must be an object, got {type(source).__name__}"]
    if status in _SOURCED_STATUSES and not source:
        return [f"verification {status!r} requires a non-empty 'source' object"]
    return []


def count_by_status(cases: list[dict[str, object]]) -> dict[str, int]:
    """Count cases per verification status.

    Returns:
        A mapping with one entry per known status, in canonical order.
    """
    counts = Counter(case.get("verification") for case in cases)
    return {status: counts[status] for status in VERIFICATION_STATUSES}
