"""Hand oracle: the final settlement of a first- or third-level apprentice.

Industria alimentare, CCNL 2023-2027 art. 21 B and C (FLAI text sha256
11792ad3…), June 2026.  The employment runs from 1 September 2025 to 30
June 2026: the June run pays the month and the ratei of the thirteenth,
6/12 of January to June.

- Month: 60 school, 20 training and 80 work hours, (80 x 0.55 + 20 x 0.20)
  / 160 = 0.30 of T.E.M. 1,746.84 and I.A.R. 95.26 at level 3A: 524.05 and
  28.58.
- Ratei: 100 work hours over the period, 0.55: 960.76 and 52.39; the
  thirteenth is (960.76 + 52.39) / 2 = 506.575 -> 506.58.  At the month's
  hours it would be (524.05 + 28.58) / 2 = 276.32.
"""

from __future__ import annotations

from dataclasses import replace
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
from ccnl_engine.apprenticeship.dual.settlement import ratei_apprentice
from ccnl_engine.employment.apprentice.inputs import (
    Apprentice,
    ApprenticeshipProgramme,
    DualHours,
)
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.employment.inputs import Permanent
from ccnl_engine.errors import InvalidInputError, MissingRequiredFactError
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.interchange.request.serializers import (
    request_from_json,
    request_to_json,
)
from ccnl_engine.seniority.inputs import SeniorityPromotion

_FIRST = ApprenticeshipProgramme.FIRST_LEVEL
_MONTH = DualHours(Decimal(60), Decimal(20), Decimal(80))
_WORK = DualHours(Decimal(0), Decimal(0), Decimal(100))
_HIRED = date(2025, 9, 1)
_THIRTEENTH = "extra_month_thirteenth_2026-06-regular"


def _input(
    apprentice: Apprentice, level: str = "3", promoted_from: str | None = None
) -> PeriodInput:
    seniority = SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS)
    if promoted_from is not None:
        promotion = SeniorityPromotion(date(2026, 6, 16), promoted_from)
        seniority = replace(seniority, promotion=promotion)
    return PeriodInput(
        run=PayrollRun.regular(2026, 6),
        payment_date=date(2026, 6, 27),
        employment=Employment(
            ccnl_id="alimentari-federalimentare",
            level_code=level,
            contract_type=apprentice,
            employment_period=EmploymentPeriod(_HIRED, date(2026, 6, 30)),
            seniority=seniority,
            pension_fund=NoPensionFund(),
            category=WorkerCategory.OPERAIO,
        ),
        employer=EmployerProfile(headcount=Headcount(60), subsector="carni"),
    )


def _qualifica(ratei_hours: DualHours | None) -> Apprentice:
    return Apprentice(
        9,
        programme=_FIRST,
        track="qualifica",
        school_year=2,
        hours=_MONTH,
        ratei_hours=ratei_hours,
    )


def _pay(request: PeriodInput) -> dict[str, Decimal]:
    result = PayrollEngine.bundled().calculate_period(request)
    assert "dual_final_settlement_hours" not in {lim.id for lim in result.limitations}
    return {i.item_id: i.amount for i in result.pay_items}


@pytest.mark.parametrize(
    ("ratei_hours", "thirteenth"),
    [(_WORK, Decimal("506.58")), (_MONTH, Decimal("276.32"))],
)
def test_the_ratei_take_their_own_hours(
    ratei_hours: DualHours, thirteenth: Decimal
) -> None:
    """The month at the hours of the month, the thirteenth at those of the ratei."""
    pay = _pay(_input(_qualifica(ratei_hours)))
    assert pay["base_salary_2026-06-regular"] == Decimal("524.05")
    assert pay["allowance_IAR_2026-06-regular"] == Decimal("28.58")
    assert pay[_THIRTEENTH] == thirteenth


def test_a_settlement_without_the_ratei_hours_blocks() -> None:
    """The month's hours would weigh the ratei by a share they did not accrue at."""
    with pytest.raises(MissingRequiredFactError, match="ratei accrued over"):
        PayrollEngine.bundled().calculate_period(_input(_qualifica(None)))


def test_the_ratei_follow_the_promotion_of_the_month() -> None:
    """Third level, 12-month programme: one level below the destination.

    Promoted to level 2 on 16 June: 11 of the 22 working days of June at
    the pay of 3A, the rest at that of 4, full work hours.  Each element is
    blended at 0.5 and rounded: base 722.83 + 873.42 = 1,596.25, contingenza
    260.00 + 262.92 = 522.92, EDR 5.17 + 5.17 = 10.34, I.A.R. 39.42 + 47.63
    = 87.05; the thirteenth at 6/12, each element rounded: 798.13 + 261.46 +
    5.17 + 43.53 = 1,108.29.  Level 2 alone would give 1,189.13.
    """
    apprentice = Apprentice(
        9,
        programme=ApprenticeshipProgramme.THIRD_LEVEL,
        programme_months=12,
        hours=_MONTH,
        ratei_hours=_WORK,
    )
    pay = _pay(_input(apprentice, level="2", promoted_from="3"))
    assert pay[_THIRTEENTH] == Decimal("1108.29")


def test_no_ratei_leave_the_contract_as_it_is() -> None:
    """A run liquidating no ratei, or another contract, reads no ratei hours."""
    assert ratei_apprentice(_qualifica(None), (), "x") is None
    assert ratei_apprentice(Permanent(), (), "x") is None
    professionalising = Apprentice(9)
    assert ratei_apprentice(professionalising, (), "x") is None


def test_the_ratei_hours_are_dual_hours() -> None:
    """Any other value is rejected."""
    with pytest.raises(InvalidInputError, match="ratei_hours"):
        Apprentice(9, programme=_FIRST, ratei_hours=100)  # type: ignore[arg-type]


def test_the_request_keeps_the_ratei_hours() -> None:
    """A stored request reads back the same apprentice."""
    request = _input(_qualifica(_WORK))
    assert request_from_json(request_to_json(request), PeriodInput) == request
