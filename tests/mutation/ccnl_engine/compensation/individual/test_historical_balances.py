"""Hand oracle for six worker-specific historical monthly balances.

In January 2026 each worker has a preserved 100.00 EUR monthly balance:
without the caller's element, the historical component is 0.00 EUR; with
it, it is 100.00 EUR (difference 100.00 EUR). These are illustrative
caller facts, not amounts asserted by any of the six agreements. For FISM,
the separate 15.00 EUR level-I Art. 46 allowance remains unchanged, so the
monthly seniority total moves from 15.00 to 115.00 EUR. The Sport
Art. 116(b) element is excluded from the thirteenth by Arts. 117 and 125;
the other three are included. The declining 14th-derived Sport element is
not tested here: its dated schedule is not given by the agreement.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
)
from ccnl_engine.inputs import (
    EmploymentPeriod,
    IndividualElement,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)


@pytest.mark.parametrize(
    ("agreement", "level", "code", "extra_months", "hire_date"),
    [
        ("poste-italiane-k700", "F", "legacy_ria", True, date(1990, 1, 1)),
        ("scuole-materne-fism", "I", "legacy_scatti", True, date(1990, 1, 1)),
        (
            "scuole-private-agidae",
            "L1",
            "frozen_seniority",
            True,
            date(1990, 1, 1),
        ),
        (
            "scuole-private-laiche-aninsei",
            "I",
            "pre_1998_scatti",
            True,
            date(1990, 1, 1),
        ),
        ("sanita-privata-aiop-aris", "A", "frozen_ria", True, date(1990, 1, 1)),
        (
            "impianti-sportivi-sport",
            "VI",
            "legacy_superminimo",
            False,
            date(2014, 1, 1),
        ),
    ],
)
def test_worker_balance_in_regular_month_and_thirteenth(
    agreement: str, level: str, code: str, extra_months: bool, hire_date: date
) -> None:
    """100.00 preserved monthly adds 100.00 in January, not an inferred rate."""
    element = IndividualElement(
        code=code,
        monthly=Decimal("100.00"),
        absorbable=False,
        extra_months=extra_months,
        tfr_relevant=True,
    )

    def run(payroll_run: PayrollRun, with_element: bool) -> Decimal:
        result = PayrollEngine.bundled().calculate_period(
            PeriodInput(
                run=payroll_run,
                payment_date=date(2026, payroll_run.month, 28),
                employment=Employment(
                    ccnl_id=agreement,
                    level_code=level,
                    contract_type=Permanent(),
                    employment_period=EmploymentPeriod(hire_date, None),
                    seniority=SeniorityFact.since(
                        hire_date, SenioritySource.EMPLOYER_RECORDS
                    ),
                    pension_fund=NoPensionFund(),
                    individual_elements=(element,) if with_element else (),
                ),
                employer=EmployerProfile(
                    headcount=Headcount(60), provincial_pay_element=False
                ),
            )
        )
        return sum(
            (item.amount for item in result.pay_items if code in item.item_id),
            Decimal(0),
        )

    assert run(PayrollRun.regular(2026, 1), False) == Decimal(0)
    assert run(PayrollRun.regular(2026, 1), True) == Decimal("100.00")
    assert run(PayrollRun.thirteenth(2026, 12), True) == (
        Decimal("100.00") if extra_months else Decimal(0)
    )
