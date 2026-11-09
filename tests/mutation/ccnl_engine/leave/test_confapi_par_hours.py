"""PAR entitlement: 104 base + 8 sector + 8 eligible shift + 4 from 2029.

A full-year day worker in instrumental electronics earns 104 + 8 = 112
hours in 2026; a worker on 15 weekly shifts including nights in the same
sector earns 104 + 8 + 8 = 120 hours. In 2029 each gains another 4 hours.
"""

from __future__ import annotations

import calendar
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.leave.accrual.rules import AccrualFacts, MonthService, accrue_month
from ccnl_engine.leave.balance.models import LeaveAccount
from ccnl_engine.leave.types import LeaveBucket


@pytest.mark.parametrize(
    ("year", "shifts", "expected"),
    [
        (2026, False, "112"),
        (2026, True, "120"),
        (2029, False, "116"),
        (2029, True, "124"),
    ],
)
def test_full_year_sector_day_and_shift_entitlements(
    year: int, shifts: bool, expected: str
) -> None:
    """Hand computed: 104 + sector 8 + shift (0 or 8) + 2029 (0 or 4)."""
    work = load_ccnl("metalmeccanico-confapi").work_rules
    assert work is not None
    rules = work.leave_rules
    assert rules is not None
    account = LeaveAccount()
    for month in range(1, 13):
        days = calendar.monthrange(year, month)[1]
        account = accrue_month(
            account,
            rules,
            AccrualFacts(
                year=year,
                month=month,
                service=MonthService(days, days),
                headcount=20,
                subsector="instrumental_electronics",
                qualifying_shifts=shifts,
            ),
        )
    (balance,) = [
        b for b in account.balances if b.bucket is LeaveBucket.ROL and b.year == year
    ]
    assert balance.accrued == Decimal(expected)
    assert balance.exact


def test_unknown_shift_only_makes_relevant_accrual_inexact() -> None:
    """Without a shift fact, 104 + 8 = 112, not the possible extra 8."""
    work = load_ccnl("metalmeccanico-confapi").work_rules
    assert work is not None
    rules = work.leave_rules
    assert rules is not None
    account = accrue_month(
        LeaveAccount(),
        rules,
        AccrualFacts(
            year=2026,
            month=1,
            service=MonthService(31, 31),
            headcount=20,
            subsector="instrumental_electronics",
        ),
    )
    (balance,) = [b for b in account.balances if b.bucket is LeaveBucket.ROL]
    assert balance.accrued == Decimal(112) / 12
    assert not balance.exact


@pytest.mark.parametrize(
    ("year", "subsector", "expected"),
    [(2001, "informatics", "112"), (2026, "steel", "104")],
)
def test_unknown_shift_outside_payable_clause(
    year: int, subsector: str, expected: str
) -> None:
    """Before 2002 or in steel, no unknown shift leave: 104 (+ 8 in informatics)."""
    work = load_ccnl("metalmeccanico-confapi").work_rules
    assert work is not None
    assert work.leave_rules is not None
    account = accrue_month(
        LeaveAccount(),
        work.leave_rules,
        AccrualFacts(
            year=year,
            month=1,
            service=MonthService(31, 31),
            headcount=20,
            subsector=subsector,
        ),
    )
    (balance,) = [b for b in account.balances if b.bucket is LeaveBucket.ROL]
    assert balance.accrued == Decimal(expected) / 12
    assert balance.exact
