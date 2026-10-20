"""Overtime of the CCNL lavoro domestico: the supplements of Art. 15.

Source: CCNL sulla disciplina del rapporto di lavoro domestico of 28 October
2025 (https://lavorodomestico.assindatcolf.it/wp-content/uploads/2026/04/
CCNL.pdf), Art. 15 (pp. 26-27):

- c. 3: overtime is paid with the hourly retribuzione globale di fatto
  "del 25%, se prestato dalle ore 6.00 alle ore 22.00; del 50%, se prestato
  dalle ore 22.00 alle ore 6.00; del 60% in una delle festività [...] o
  nella giornata di domenica";
- c. 4: the hours of non conviventi from the 41st to the 44th of the week,
  by day, are paid with a 10% supplement.

Two overtime hours at 10.00 an hour.  A non convivente event without its
hours of the week takes the first tier, 10%, and the run reports the tier
left out.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    InvalidInputError,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.events import OvertimeEvent, OvertimeKind
from ccnl_engine.inputs import ContributableHours, Permanent, WeeklyHours
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

pytestmark = pytest.mark.legal_scenario

_ENGINE = PayrollEngine.bundled()
_CONVIVENTE = "lavoro-domestico-convivente"
_NON_CONVIVENTE = "lavoro-domestico-non-convivente"


def _run(slug: str, kind: OvertimeKind) -> PeriodResult:
    weekly = 54 if slug == _CONVIVENTE else 40
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id=slug,
                level_code="CS",
                seniority=new_hire(),
                weekly_hours=WeeklyHours(Decimal(weekly)),
                full_time_weekly_hours=WeeklyHours(Decimal(weekly)),
                contract_type=Permanent(),
            ),
            employer=EmployerProfile(headcount=Headcount(1)),
            facts=PeriodFacts(
                contributable_hours=ContributableHours(Decimal(200)),
                events=(
                    OvertimeEvent(
                        date(2026, 3, 10), Decimal(2), Decimal("10.00"), kind=kind
                    ),
                ),
            ),
        )
    )


def _overtime(result: PeriodResult) -> Decimal:
    return sum(
        (i.amount for i in result.pay_items if i.kind == "overtime_earning"),
        Decimal(0),
    )


@pytest.mark.parametrize(
    ("slug", "kind", "amount"),
    [
        (_CONVIVENTE, OvertimeKind.WEEKDAY, Decimal("25.00")),
        (_CONVIVENTE, OvertimeKind.NIGHT, Decimal("30.00")),
        (_CONVIVENTE, OvertimeKind.HOLIDAY, Decimal("32.00")),
        (_NON_CONVIVENTE, OvertimeKind.NIGHT, Decimal("30.00")),
        (_NON_CONVIVENTE, OvertimeKind.HOLIDAY, Decimal("32.00")),
    ],
)
def test_art_15_supplements(slug: str, kind: OvertimeKind, amount: Decimal) -> None:
    """2 x 10.00 x 1.25, 1.50 and 1.60."""
    assert _overtime(_run(slug, kind)) == amount


def test_non_convivente_first_tier_is_ten_percent() -> None:
    """Hours 41 to 44: 2 x 10.00 x 1.10 = 22.00, the 25% tier left out."""
    result = _run(_NON_CONVIVENTE, OvertimeKind.WEEKDAY)

    assert _overtime(result) == Decimal("22.00")
    assert "overtime_tier_not_applied" in {issue.code for issue in result.issues}


def test_night_overtime_on_a_holiday_has_no_band() -> None:
    """Art. 15 sets no rate of its own for it: the event needs a multiplier."""
    with pytest.raises(InvalidInputError, match="no multiplier"):
        _run(_CONVIVENTE, OvertimeKind.NIGHT_HOLIDAY)
