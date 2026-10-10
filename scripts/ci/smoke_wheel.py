"""Wheel smoke test: import the engine and run one end-to-end scenario.

This script is intentionally dependency-minimal so it can run in a clean
virtual environment that has only the installed wheel (no dev extras).
It exercises the public API surface and exits non-zero on any failure.
"""

from __future__ import annotations

import gzip
import json
import sys
from datetime import date
from decimal import Decimal
from importlib.resources import files
from pathlib import Path

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
)
from ccnl_engine.catalog import get_ccnl
from ccnl_engine.inputs import Permanent


def main() -> int:
    """Run the smoke test; return 0 on success, 1 on failure.

    Returns:
        0 when the end-to-end scenario produces a positive period_net;
        1 on any exception or unexpected result.
    """
    engine = PayrollEngine.bundled()
    request = PeriodInput(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        employment=Employment(
            ccnl_slug="agenti-immobiliari-fiaip.json",
            level_code="II",
            contract_type=Permanent(),
        ),
        employer=EmployerProfile(headcount=Headcount(50)),
    )
    try:
        result = engine.calculate_period(request)
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: engine.calculate_period() raised {type(exc).__name__}: {exc}")
        return 1

    net = result.period_net
    if net <= Decimal(0):
        print(f"FAIL: period_net is {net!r}, expected > 0")
        return 1

    print(f"OK: period_net={net}")

    ccnls = engine.list_contracts()
    if len(ccnls) != 126:
        print(f"FAIL: list_contracts() returned {len(ccnls)} items, expected 126")
        return 1

    slug = ccnls[0].ccnl_id
    by_slug = get_ccnl(slug)
    by_code = get_ccnl(by_slug.cnel_code)
    if by_slug != by_code:
        print("FAIL: get_ccnl by slug and by CNEL code returned different results")
        return 1

    ruleset = engine.inspect_ruleset(slug)
    if ruleset.readiness is not by_slug.readiness:
        print("FAIL: inspect_ruleset and list_contracts disagree on readiness")
        return 1

    print(f"OK: list_contracts()={len(ccnls)}, '{slug}' is {ruleset.readiness}")
    return _knowledge_parity()


_MANIFEST = "manifest.json"


def _installed(path: str) -> object:
    """Return the JSON of a knowledge resource as the wheel stores it.

    Returns:
        The decoded ``<path>.gz`` of the installed package.
    """
    packed = files("ccnl_engine.knowledge").joinpath(*f"{path}.gz".split("/"))
    return json.loads(gzip.decompress(packed.read_bytes()).decode("utf-8"))


def _knowledge_parity() -> int:
    """Check that the wheel holds the source bundle, resource for resource.

    The installed manifest must equal the source one, and every resource it
    lists must decode to the JSON of the source file.

    Returns:
        0 when the list and the content match; 1 otherwise.
    """
    source = Path("src/ccnl_engine/knowledge")
    expected = json.loads((source / _MANIFEST).read_text(encoding="utf-8"))
    if _installed(_MANIFEST) != expected:
        print("FAIL: the installed knowledge manifest differs from the source one")
        return 1
    for entry in expected["resources"]:
        path = entry["path"]
        if _installed(path) != json.loads((source / path).read_text("utf-8")):
            print(f"FAIL: {path} in the wheel differs from the source file")
            return 1
    print(f"OK: {len(expected['resources'])} knowledge resources match the source")
    return 0


if __name__ == "__main__":
    sys.exit(main())
