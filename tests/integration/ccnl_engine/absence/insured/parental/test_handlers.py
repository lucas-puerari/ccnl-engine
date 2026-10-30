"""The parental leave, paid by INPS at its rate on the pay of the month before.

Metalmeccanico Federmeccanica C3 impiegato, 2158.26 EUR a month, daily
quota by 26; February paid 2400.00 with 13 monthly payments a year, so the
RMGG of art. 23 D.Lgs. 151/2001 is (2400 + 2400 / 12) / 30 = 86.666667.
By hand (art. 34 c. 1):

- the whole of March, child born on 1 June 2025, maternity ended on 1
  September 2025 (three months of the couple at 80%), nothing taken: the
  calendar month is one month at 80%, its 31 days paid 86.666667 * 0.80 *
  31 = 2149.33; the whole monthly pay 2158.26 is deducted;
- the same with 80 days already taken, all at 80%: 10 days at 80% and 21
  at 30%, 86.666667 * (8 + 6.3) = 1239.33;
- 2-13 March, child born in 2022 and no maternity end stated: no month at
  80% the birth gives, 12 days at 30%, 86.666667 * 3.6 = 312.00; 11 CCNL
  days deducted, 2158.26 * 11 / 26 = 913.11.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.events import (
    InpsSicknessBase,
    ParentalLeaveEvent,
    ParentalLeaveTaken,
    WorkEvent,
)
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult

_HIRED = date(2025, 1, 1)
_FEBRUARY = InpsSicknessBase(Decimal(2400), Decimal(0))
_BORN = date(2025, 6, 1)
_MATERNITY_END = date(2025, 9, 1)
_NOTHING = ParentalLeaveTaken(0, 0, 0)


def _march(
    taken: ParentalLeaveTaken = _NOTHING,
    *,
    base: InpsSicknessBase | None = _FEBRUARY,
) -> ParentalLeaveEvent:
    return ParentalLeaveEvent(
        date(2026, 3, 1),
        date(2026, 3, 31),
        _BORN,
        taken,
        _MATERNITY_END,
        parental_base_pay=base,
    )


def _run(
    *events: WorkEvent, category: WorkerCategory = WorkerCategory.IMPIEGATO
) -> PeriodResult:
    """Return March 2026 with ``events``.

    Returns:
        The result of the run.
    """
    return PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id="metalmeccanico-federmeccanica",
                level_code="C3",
                category=category,
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
                tfr_treasury_fund=False,
            ),
            employer=EmployerProfile(headcount=Headcount(20)),
            facts=PeriodFacts(events=events),
        )
    )


def _amounts(result: PeriodResult) -> dict[str, tuple[str, Decimal]]:
    return {
        i.kind: (i.item_id.rsplit("_", 1)[-1], i.amount)
        for i in result.pay_items
        if "_evt" in i.item_id
    }


def _limitations(result: PeriodResult) -> set[str]:
    return {lim.id for lim in result.limitations if lim.id.startswith("parental")}


def test_a_whole_month_at_80_percent() -> None:
    """A calendar month is one month: its 31 days are paid at 80%."""
    result = _run(_march())

    assert _amounts(result) == {
        "absence_deduction": ("abs", Decimal("2158.26")),
        "maternity_item": ("inps", Decimal("2149.33")),
    }
    (decision,) = (d for d in result.decisions if d.capability == "parental_leave")
    assert (decision.amount, decision.status) == (Decimal("2149.33"), "provisional")
    (item,) = (i for i in result.pay_items if i.kind == "maternity_item")
    assert item.absence_days == Decimal(31)
    assert ("insured_absence_ccnl_not_modelled", "parental_leave") in {
        (i.code, i.capability) for i in result.issues
    }
    assert _limitations(result) == set()


def test_the_80_percent_months_run_out_inside_the_month() -> None:
    """The last 10 days at 80%, then the shared months at 30%."""
    result = _run(_march(ParentalLeaveTaken(80, 80, 0)))

    assert _amounts(result)["maternity_item"] == ("inps", Decimal("1239.33"))
    assert _limitations(result) == {"parental_month_split"}


def test_the_days_beyond_the_indemnified_months_are_not_paid() -> None:
    """The income condition of c. 3 is not modelled: the engine says so."""
    taken = ParentalLeaveTaken(90, 90, 90)

    result = _run(_march(taken))

    assert "maternity_item" not in _amounts(result)
    assert _limitations(result) == {"parental_income_condition"}


def test_an_unstated_end_of_the_maternity_leave_is_a_missing_fact() -> None:
    """Born in 2022: only a late end of the maternity gives 80% months."""
    leave = ParentalLeaveEvent(
        date(2026, 3, 2),
        date(2026, 3, 13),
        date(2022, 6, 1),
        _NOTHING,
        parental_base_pay=_FEBRUARY,
    )

    result = _run(leave)

    assert _amounts(result) == {
        "absence_deduction": ("abs", Decimal("913.11")),
        "maternity_item": ("inps", Decimal("312.00")),
    }
    assert ("missing_fact", "protection_ended_on") in {
        (b.code, b.detail) for b in result.blockers
    }
    (issue,) = (i for i in result.issues if i.code == "parental_protection_end_unknown")
    assert (issue.capability, issue.fact) == ("parental_leave", "protection_ended_on")


def test_without_the_pay_before_a_fact_is_missing() -> None:
    """The base is a fact of the payroll history: its absence blocks."""
    result = _run(_march(base=None))

    (issue,) = (i for i in result.issues if i.code == "parental_base_pay_unknown")
    assert (issue.capability, issue.fact) == ("parental_leave", "parental_base_pay")
    assert "ParentalLeaveEvent.parental_base_pay" in issue.message
    # The pay of the run: (2158.26 + 2158.26 / 12) / 30 * 0.80 * 31 = 1932.84.
    assert _amounts(result)["maternity_item"] == ("inps", Decimal("1932.84"))


def test_an_operaio_keeps_the_pay_of_the_run_under_a_limitation() -> None:
    """Art. 23 c. 5 is not computed: the engine says so."""
    result = _run(_march(), category=WorkerCategory.OPERAIO)

    assert _limitations(result) == {"parental_daily_base"}


def test_the_leave_keeps_the_13th_and_the_leave_accrual_not_the_tfr() -> None:
    """Art. 34 c. 5; art. 2120 c. 3 c.c. keeps no parental leave in the TFR."""
    worked, away = _run(), _run(_march())

    assert away.extra_months == worked.extra_months
    assert away.closing_state.accrual.leave == worked.closing_state.accrual.leave
    (tfr,) = (d.amount for d in away.decisions if d.capability == "tfr")
    assert tfr == Decimal(0)


def test_the_leave_ends_before_the_child_is_fourteen() -> None:
    """Art. 32 c. 1: the leave is due in the first fourteen years."""
    leave = ParentalLeaveEvent(
        date(2026, 3, 1),
        date(2026, 3, 31),
        date(2012, 3, 15),
        _NOTHING,
        parental_base_pay=_FEBRUARY,
    )

    with pytest.raises(InvalidInputError, match="14th birthday"):
        _run(leave)
