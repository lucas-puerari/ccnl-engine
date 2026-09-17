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
    Agreement,
    Employee,
    Employer,
    Employment,
    PayrollScenario,
    Permanent,
    RalOverride,
    SeniorityByDate,
    compute,
)


def main() -> int:
    """Run the smoke test; return 0 on success, 1 on failure.

    Returns:
        0 when the end-to-end scenario produces a positive net_annual;
        1 on any exception or unexpected result.
    """
    scenario = PayrollScenario(
        employee=Employee(
            level_code="II",
            seniority=SeniorityByDate(value=date(2020, 1, 1)),
            weekly_hours=Decimal(40),
            agreement=Agreement(ral_override=RalOverride(value=Decimal(30000))),
        ),
        employment=Employment(
            ccnl="agenti-immobiliari-fiaip.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            calculation_date=date(2026, 1, 1),
        ),
    )
    try:
        result = compute(scenario)
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: compute() raised {type(exc).__name__}: {exc}")
        return 1

    net = result.result.net_annual
    if net <= Decimal(0):
        print(f"FAIL: net_annual is {net!r}, expected > 0")
        return 1

    print(f"OK: net_annual={net}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
