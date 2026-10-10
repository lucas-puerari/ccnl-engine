"""Conviventi with fewer hours: the art. 14 c. 2 regime and art. 14 c. 1.

CCNL sulla disciplina del rapporto di lavoro domestico of 28 October 2025
(https://lavorodomestico.assindatcolf.it/wp-content/uploads/2026/04/
CCNL.pdf), art. 14:

- c. 1: the normal hours of a convivente are agreed, "con un massimo di
  [...] 54 ore settimanali"; Tabella A gives monthly values and no rule
  to proportion them to fewer agreed hours;
- c. 2: conviventi of levels C, B and B super "possono essere assunti in
  regime di convivenza anche con orario fino a 30 ore settimanali" and are
  paid, "qualunque sia l'orario di lavoro osservato nel limite massimo
  delle 30 ore settimanali", the Tabella B minimum, board and lodging in
  full.

Tabella minimi retributivi 2026: Tabella B, level B super 737.39 a month;
Tabella A, level C super 1,193.84 a month.

INPS 2026 for up to 24 weekly hours (circ. 9/2026, bundled table): worker
share 0.43 EUR an hour up to an hourly pay of 9.61, 0.48 up to 11.70, 0.59
above.  The hourly pay of a Tabella B worker is the flat monthly pay over
the hours worked: at 10 weekly hours 737.39 / (10 x 52 / 12 = 43.33) =
17.02, at 20 hours 737.39 / 86.67 = 8.51.
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
from ccnl_engine.inputs import ContributableHours, Permanent, WeeklyHours
from tests.knowledge.ccnl_engine.payroll.employment.builders_seniority import new_hire

pytestmark = pytest.mark.legal_scenario

_ENGINE = PayrollEngine.bundled()
_REDUCED = "lavoro-domestico-convivente-orario-ridotto.json"
_CONVIVENTE = "lavoro-domestico-convivente.json"


def _march(slug: str, level: str, weekly: int, full_time: int | None) -> PeriodResult:
    employment = Employment(
        ccnl_slug=slug,
        level_code=level,
        seniority=new_hire(),
        weekly_hours=WeeklyHours(weekly),
        full_time_weekly_hours=None if full_time is None else WeeklyHours(full_time),
        contract_type=Permanent(),
    )
    hours = ContributableHours(Decimal(weekly * 52) / 12)
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 20),
            employment=employment,
            employer=EmployerProfile(headcount=Headcount(1)),
            facts=PeriodFacts(contributable_hours=hours),
        )
    )


@pytest.mark.parametrize("weekly", [20, 30])
def test_tabella_b_is_paid_whatever_the_hours(weekly: int) -> None:
    """B super under art. 14 c. 2: 737.39 at 20 and at 30 weekly hours."""
    result = _march(_REDUCED, "BS", weekly, None)
    assert result.period_gross == Decimal("737.39")
    assert "full_time_hours_unknown" not in {i.code for i in result.issues}


def test_more_than_30_hours_is_not_the_reduced_regime() -> None:
    """31 weekly hours exceed the ceiling of art. 14 c. 2."""
    with pytest.raises(InvalidInputError, match="up to 30 weekly hours"):
        _march(_REDUCED, "BS", 31, None)


def test_fewer_agreed_hours_under_c_1_block_the_run() -> None:
    """C super, 40 of 54 hours: 1,193.84 x 40 / 54 = 884.3259 -> 884.33.

    The CCNL gives no rule for it: the linear amount is shown and the open
    limitation keeps the run from being paid.
    """
    result = _march(_CONVIVENTE, "CS", 40, 54)
    ids = {limitation.id for limitation in result.assurance.limitations}
    assert result.period_gross == Decimal("884.33")
    assert "lavoro-domestico-convivente/part_time_scaling" in ids
    assert not result.is_payable


def test_full_time_convivente_traverses_no_scaling() -> None:
    """C super at 54 of 54 hours is paid Tabella A without the limitation."""
    result = _march(_CONVIVENTE, "CS", 54, 54)
    ids = {limitation.id for limitation in result.assurance.limitations}
    assert result.period_gross == Decimal("1193.84")
    assert "lavoro-domestico-convivente/part_time_scaling" not in ids


@pytest.mark.parametrize(
    ("weekly", "per_hour"),
    [(10, Decimal("0.59")), (20, Decimal("0.43"))],
)
def test_inps_bracket_reads_the_hours_worked(weekly: int, per_hour: Decimal) -> None:
    """The hourly pay is the flat pay over the hours worked, not over 30."""
    result = _march(_REDUCED, "BS", weekly, None)
    hours = Decimal(weekly * 52) / 12
    expected = (per_hour * hours).quantize(Decimal("0.01"))
    assert result.contribution_breakdown.employee == expected
