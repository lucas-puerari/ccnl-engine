"""Sick pay of the CCNL lavoro domestico: the employer pays, days counted in a year.

Source: CCNL sulla disciplina del rapporto di lavoro domestico of 28 October
2025 (https://lavorodomestico.assindatcolf.it/wp-content/uploads/2026/04/
CCNL.pdf), Art. 27 (pp. 37-38) and chiarimento a verbale 2 (p. 56):

- c. 4: the job is kept "per anzianità oltre i 2 anni, 180 giorni di
  calendario";
- c. 7: "decorre in caso di malattia la retribuzione globale di fatto per
  un massimo di 8, 10, 15 giorni complessivi nell'anno [...] fino al 3°
  giorno consecutivo, il 50% [...] dal 4° giorno in poi, il 100%";
- chiarimento 2: "giorni di calendario" are thirtieths of the monthly pay,
  "esempio: malattia".

INPS pays no sickness indemnity to colf and badanti (INPS, Indennità di
malattia per lavoratori dipendenti: "Non spetta a [...] collaboratori
familiari (colf e badanti)").

Convivente level CS, Tabella A 1,193.84, one seniority step of 47.75 (36
months of seniority): 1,241.59 a month, 41.386 a day.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

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
from ccnl_engine.events import SicknessEpisode
from ccnl_engine.inputs import (
    ContributableHours,
    EmploymentPeriod,
    Permanent,
    SeniorityFact,
    SenioritySource,
    WeeklyHours,
)

_ENGINE = PayrollEngine.bundled()


def _march(last: date) -> PeriodResult:
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id="lavoro-domestico-convivente",
                level_code="CS",
                seniority=SeniorityFact(36, date(2026, 1, 1), SenioritySource.PAYSLIP),
                weekly_hours=WeeklyHours(54),
                full_time_weekly_hours=WeeklyHours(54),
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(date(2023, 1, 1)),
            ),
            employer=EmployerProfile(headcount=Headcount(1)),
            facts=PeriodFacts(
                contributable_hours=ContributableHours(Decimal(234)),
                events=(SicknessEpisode("A", date(2026, 3, 2), last),),
            ),
        )
    )


def _by_kind(result: PeriodResult) -> dict[str, Decimal]:
    totals: dict[str, Decimal] = {}
    for item in result.pay_items:
        if "_evt" in item.item_id:
            totals[item.kind] = totals.get(item.kind, Decimal(0)) + item.amount
    return totals


def test_five_days_half_pay_then_full_pay() -> None:
    """2-6 March: 1,241.59 * 5 / 30 = 206.93 deducted.

    Days 1-3 at 50%: 1,241.59 * 3 / 30 * 0.5 = 62.08; days 4-5 in full:
    1,241.59 * 2 / 30 = 82.77.  INPS pays nothing.
    """
    assert _by_kind(_march(date(2026, 3, 6))) == {
        "absence_deduction": Decimal("206.93"),
        "sickness_item": Decimal("144.85"),
    }


def test_days_past_the_fifteenth_are_unpaid() -> None:
    """2-21 March: 20 days, 3 at 50% and 12 in full, the last 5 unpaid.

    Deducted by component: 1,193.84 * 20 / 30 = 795.89 and 47.75 * 20 / 30
    = 31.83, together 827.72; paid 62.08 + 1,241.59 * 12 / 30 = 496.64.
    """
    result = _march(date(2026, 3, 21))

    assert _by_kind(result) == {
        "absence_deduction": Decimal("827.72"),
        "sickness_item": Decimal("558.72"),
    }
    (decision,) = (d for d in result.decisions if d.capability == "sickness")
    assert decision.inputs["divisor_method"] == "by_30"
    assert decision.inputs["inps_cover"] == "false"
    assert decision.inputs["band_full_pay_days"] == Decimal(15)
