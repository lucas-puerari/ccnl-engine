"""CED, Fiori and Ortofrutticoli funds, paid or replaced by their element.

CED art. 221 (EBCE 8 + 3 EUR, else 26 EUR) and art. 268 (EASI 15 + 2 EUR,
else 36 EUR); Fiori art. 54 (Fondo EST 10 + 2 EUR, else 16 EUR);
Ortofrutticoli art. 23 (Fondo EST 10 EUR by the employer). Health funds
carry the 10% INPS solidarity contribution on the employer share.
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
from ccnl_engine.inputs import EmploymentPeriod, NoPensionFund, Permanent


def _funds(slug: str, level: str, funds: frozenset[str]) -> dict[str, Decimal]:
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id=slug,
                level_code=level,
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(date(2020, 1, 1), None),
                pension_fund=NoPensionFund(),
            ),
            employer=EmployerProfile(headcount=Headcount(10), contractual_funds=funds),
        )
    )
    return {
        i.item_id.replace("_2026-03-regular", ""): i.amount
        for i in result.pay_items
        if i.item_id.startswith(("ebce", "easi", "fondo_est"))
    }


@pytest.mark.parametrize(
    ("slug", "level", "funds", "paid"),
    [
        (
            "ced-assoced",
            "3",
            frozenset({"ebce", "easi"}),
            {
                "ebce_er": "8.00",
                "ebce_emp": "3.00",
                "easi_er": "15.00",
                "easi_emp": "2.00",
                "easi_solidarity": "1.50",
            },
        ),
        (
            "ced-assoced",
            "3",
            frozenset(),
            {"ebce_element": "26.00", "easi_element": "36.00"},
        ),
        (
            "fiori-recisi-ancef",
            "3",
            frozenset({"fondo_est"}),
            {
                "fondo_est_er": "10.00",
                "fondo_est_emp": "2.00",
                "fondo_est_solidarity": "1.00",
            },
        ),
        ("fiori-recisi-ancef", "3", frozenset(), {"fondo_est_element": "16.00"}),
        (
            "ortofrutticoli-agrumari",
            "4",
            frozenset({"fondo_est"}),
            {"fondo_est_er": "10.00", "fondo_est_solidarity": "1.00"},
        ),
    ],
)
def test_the_fund_or_its_element(
    slug: str, level: str, funds: frozenset[str], paid: dict[str, str]
) -> None:
    """The employer pays the fund it names, else the element in its place."""
    assert _funds(slug, level, funds) == {k: Decimal(v) for k, v in paid.items()}
