"""Hand oracle: the bilateral system and the health fund of Unionmeccanica Confapi.

5th level, minimo 2,245.87 EUR from 1 June 2026.

- E.B.M. (art. 53; the fund's sheet "Modalità di contribuzione"): 6 EUR a
  month from a firm without an internal RLS, 5 EUR with one; 5.75 and 4.75
  for a part-timer of at most 20 hours a week.  A firm that does not adhere
  owes the E.A.R. of 25 EUR for 13 months, proportional to the hours and
  outside the TFR (CCNL 2017, p. 131).
- EBM Salute (art. 51, accordo 4 June 2026 p. 22): 8 EUR a month from the
  employer from 2022, a health fund (10% INPS solidarity), no element.
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
    PeriodResult,
)
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
    WeeklyHours,
)
from ccnl_engine.results import AccountKind

_HIRED = date(2026, 1, 1)


def _run(
    funds: frozenset[str],
    *,
    hours: int | None = None,
    thirteenth: bool = False,
) -> PeriodResult:
    return PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.thirteenth(2026, 12)
            if thirteenth
            else PayrollRun.regular(2026, 6),
            payment_date=date(2026, 12, 15) if thirteenth else date(2026, 6, 27),
            employment=Employment(
                ccnl_id="metalmeccanico-confapi",
                level_code="5",
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
                weekly_hours=None if hours is None else WeeklyHours(Decimal(hours)),
                full_time_weekly_hours=None
                if hours is None
                else WeeklyHours(Decimal(40)),
            ),
            employer=EmployerProfile(headcount=Headcount(60), contractual_funds=funds),
        )
    )


def _posted(result: PeriodResult, account: AccountKind) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account is account), Decimal(0)
    )


def _elements(result: PeriodResult) -> list[Decimal]:
    return [i.amount for i in result.pay_items if "_element_" in i.item_id]


@pytest.mark.parametrize(
    ("funds", "employer"),
    [
        (frozenset({"ebm", "ebm_salute"}), Decimal("14.00")),
        (frozenset({"ebm_rls", "ebm_salute"}), Decimal("13.00")),
    ],
)
def test_a_firm_that_adheres(funds: frozenset[str], employer: Decimal) -> None:
    """EBM 6 (or 5 with an RLS) plus EBM Salute 8; 0.80 solidarity."""
    result = _run(funds)

    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYER) == employer
    solidarity = [
        e.amount for e in result.ledger_entries if e.entry_id.endswith("_solidarity")
    ]
    assert solidarity == [Decimal("0.80")]
    assert _elements(result) == []


def test_a_short_part_timer_pays_the_reduced_share() -> None:
    """20 hours a week: 5.75 EUR to the EBM, plus the 8 EUR of EBM Salute."""
    result = _run(frozenset({"ebm"}), hours=20)

    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYER) == Decimal("13.75")


def test_a_firm_that_does_not_adhere_owes_the_ear_once() -> None:
    """One E.A.R. of 25 EUR for the group, also on the 13th; half at 20 hours."""
    assert _elements(_run(frozenset())) == [Decimal("25.00")]
    assert _elements(_run(frozenset(), thirteenth=True)) == [Decimal("25.00")]
    assert _elements(_run(frozenset(), hours=20)) == [Decimal("12.50")]
