"""Domestic INPS bands read the paga oraria effettiva; the tredicesima has no hours.

INPS circolare n. 9 of 3 February 2026, par. 2, table A (https://www.inps.it/
content/dam/inps-site/it/scorporati/circolari-e-messaggi/2026/02/
Circolare_15154/Allegati/16551_Circolare-numero-9-del-03-02-2026.pdf): up to
24 weekly hours the hourly contribution is 1.70 (0.43 the worker's) up to an
effective hourly pay of 9.61, 1.92 (0.48) up to 11.70, 2.34 (0.59) above.

INPS page Contributi e agevolazioni fiscali per chi assume un lavoratore
domestico (https://www.inps.it/it/it/dettaglio-approfondimento.schede-
informative.49828.contributi-e-agevolazioni-fiscali-per-chi-assume-un-
lavoratore-domestico.html): "La paga oraria effettiva è composta da: la
retribuzione oraria concordata tra le parti; il valore convenzionale del
vitto e alloggio, ripartito per ore; la tredicesima mensilità (gratifica
natalizia), ripartita per ore."

Tabella C 2026 (CCNL lavoro domestico of 28 October 2025, p. 59): level A
6.51 an hour, level DS 9.97.  At 20 weekly hours the effective pay is
6.51 x 13 / 12 = 7.05 (first band) and 9.97 x 13 / 12 = 10.80 (second band:
the agreed 9.97 alone would fall in the first).
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
    PeriodFacts,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.inputs import ContributableHours, Permanent, WeeklyHours
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

pytestmark = pytest.mark.legal_scenario

_ENGINE = PayrollEngine.bundled()
_NON_CONVIVENTE = "lavoro-domestico-non-convivente.json"
_HOURS = Decimal(20 * 52) / 12


def _run(run: PayrollRun, level: str) -> PeriodResult:
    return _ENGINE.calculate_period(
        PeriodInput(
            run=run,
            payment_date=date(run.year, run.month, 20),
            employment=Employment(
                ccnl_slug=_NON_CONVIVENTE,
                level_code=level,
                seniority=new_hire(),
                weekly_hours=WeeklyHours(20),
                full_time_weekly_hours=WeeklyHours(40),
                contract_type=Permanent(),
            ),
            employer=EmployerProfile(headcount=Headcount(1)),
            facts=PeriodFacts(contributable_hours=ContributableHours(_HOURS)),
        )
    )


@pytest.mark.parametrize(
    ("level", "employee", "employer"),
    [("A", Decimal("0.43"), Decimal("1.27")), ("DS", Decimal("0.48"), Decimal("1.44"))],
)
def test_band_includes_the_tredicesima_share(
    level: str, employee: Decimal, employer: Decimal
) -> None:
    """A part-time DS falls in the second band once the tredicesima is spread."""
    result = _run(PayrollRun.regular(year=2026, month=3), level)

    rates = {c.name: c.rate for c in result.contribution_breakdown.components}
    assert rates == {
        "domestic_employee_per_hour": employee,
        "domestic_employer_per_hour": employer,
    }
    assert result.contribution_breakdown.employee == (employee * _HOURS).quantize(
        Decimal("0.01")
    )


def test_tredicesima_run_charges_no_inps_hours() -> None:
    """The tredicesima is already spread over the hours of the year."""
    result = _run(PayrollRun.thirteenth(2026, 12), "DS")

    assert result.contribution_breakdown.employee == Decimal(0)
    assert result.contribution_breakdown.employer == Decimal(0)
