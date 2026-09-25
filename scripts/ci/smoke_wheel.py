"""Wheel smoke test: import the engine and run one end-to-end scenario.

This script is intentionally dependency-minimal so it can run in a clean
virtual environment that has only the installed wheel (no dev extras).
It exercises the public API surface and exits non-zero on any failure.
"""

from __future__ import annotations

import sys
from datetime import date
from decimal import Decimal

from ccnl_engine import (
    EmploymentFacts,
    PayrollEngine,
    PayrollRequest,
    PayrollRun,
    get_ccnl,
    list_ccnls,
)


def main() -> int:
    """Run the smoke test; return 0 on success, 1 on failure.

    Returns:
        0 when the end-to-end scenario produces a positive period_net;
        1 on any exception or unexpected result.
    """
    engine = PayrollEngine.bundled()
    request = PayrollRequest(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        ccnl_slug="agenti-immobiliari-fiaip.json",
        level_code="II",
        employment_facts=EmploymentFacts(num_employees=50),
    )
    try:
        result = engine.calculate(request)
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: engine.calculate() raised {type(exc).__name__}: {exc}")
        return 1

    net = result.period_net
    if net <= Decimal(0):
        print(f"FAIL: period_net is {net!r}, expected > 0")
        return 1

    print(f"OK: period_net={net}")

    ccnls = list_ccnls()
    if len(ccnls) != 125:
        print(f"FAIL: list_ccnls() returned {len(ccnls)} items, expected 125")
        return 1

    slug = ccnls[0].ccnl_id
    by_slug = get_ccnl(slug)
    by_code = get_ccnl(by_slug.cnel_code)
    if by_slug != by_code:
        print("FAIL: get_ccnl by slug and by CNEL code returned different results")
        return 1

    print(f"OK: list_ccnls()={len(ccnls)}, get_ccnl resolved '{slug}' and CNEL code")
    return 0


if __name__ == "__main__":
    sys.exit(main())
