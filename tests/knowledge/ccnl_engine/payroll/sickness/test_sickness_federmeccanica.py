"""Sick pay of CCNL Federmeccanica: treatment chain, comporto, short absences.

Source: CCNL 5 febbraio 2021 per l'industria metalmeccanica privata e della
installazione di impianti, Sez. Quarta, Titolo VI, Art. 2 (text published by
FIOM-CGIL, https://www.fiom-cgil.it/images/CCNL/INDUSTRIA/2021_02_05-CCNL-
federmeccanica.pdf, pp. 196-199), unchanged on these points by the ipotesi
di accordo of 22 November 2025:

- "alla intera retribuzione globale per i primi 122 giorni di calendario e
  all'80% della retribuzione globale per i giorni residui, per anzianità di
  servizio fino a tre anni compiuti";
- "Il suddetto trattamento economico ricomincia ex novo in caso di malattia
  [...] intervenuto dopo un periodo di 61 giorni di calendario dalla ripresa
  del servizio";
- "i primi tre giorni della quarta e delle successive assenze di durata non
  superiore a 5 giorni saranno retribuiti [...] quarta assenza: 66% della
  intera retribuzione globale".

Metalmeccanico C3 operaio, 2158.26 EUR a month to May 2026 and 2211.43 from
June, daily quota by 26, seniority under three years.  INPS (D.L. 663/1979
art. 2, as recorded in the bundle): no indemnity on days 1-3, 50% on days
4-20, 66.66% on days 21-180 of the episode.  Amounts are rounded half up to
the cent; the worker gets the CCNL rate, INPS pays its share of it.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    CompetenceYearPlan,
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
    EmploymentPeriod,
    InpsBaseYtd,
    OpeningBalances,
    PeriodState,
    Permanent,
    SeniorityFact,
    SenioritySource,
    WorkerCategory,
)
from ccnl_engine.results import BlockerCode
from tests.integration.ccnl_engine.payroll.withholding.builders_withholding import (
    paid_before,
)
from tests.knowledge.ccnl_engine.payroll.employment.builders_seniority import new_hire

_ENGINE = PayrollEngine.bundled()
_EMPLOYER = EmployerProfile(headcount=Headcount(50))
_HIRED = date(2026, 1, 1)
_EMPLOYMENT = Employment(
    contract_type=Permanent(),
    ccnl_slug="metalmeccanico-federmeccanica.json",
    level_code="C3",
    category=WorkerCategory.OPERAIO,
    seniority=new_hire(),
    employment_period=EmploymentPeriod(_HIRED),
)


def _by_kind(result: PeriodResult) -> dict[str, Decimal]:
    totals: dict[str, Decimal] = {}
    for item in result.pay_items:
        if "_evt" in item.item_id:
            totals[item.kind] = totals.get(item.kind, Decimal(0)) + item.amount
    return totals


def _decisions(result: PeriodResult) -> list[dict[str, object]]:
    return [dict(d.inputs) for d in result.decisions if d.capability == "sickness"]


def _codes(result: PeriodResult) -> set[str]:
    return {issue.code for issue in result.issues}


def test_days_past_the_122nd_are_paid_at_80_percent() -> None:
    """Sick from Monday 5 January to Sunday 31 May 2026: the May run.

    5 January is day 1, so 1 May is day 27 + 28 + 31 + 30 + 1 = 117 and
    6 May day 122: 1-6 May are paid in full, 7-31 May at 80%.  By 26, 1-6
    May hold 5 Mondays to Saturdays and May 26, so 7-31 May hold 21:

    - deducted: 2158.26 * 5 / 26 = 415.05, and 2158.26 - 415.05 = 1743.21;
    - INPS 66.66% (days 117-147): 415.05 * 0.6666 = 276.67 and
      1743.21 * 0.6666 = 1162.02, together 1438.69;
    - employer: 415.05 - 276.67 = 138.38, and 1743.21 * 0.80 = 1394.57,
      1394.57 - 1162.02 = 232.55, together 370.93.
    """
    episode = PeriodFacts(
        events=(SicknessEpisode("A", date(2026, 1, 5), date(2026, 5, 31)),)
    )
    seniority = SeniorityFact(12, date(2026, 1, 1), SenioritySource.PAYSLIP)
    year = _ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=Employment(
                contract_type=Permanent(),
                ccnl_slug="metalmeccanico-federmeccanica.json",
                level_code="C3",
                category=WorkerCategory.OPERAIO,
                seniority=seniority,
            ),
            employer=_EMPLOYER,
            periods=dict.fromkeys(range(1, 6), episode),
            payment_day=27,
        )
    )
    may = next(r for r in year.period_results if r.run == PayrollRun.regular(2026, 5))
    assert _by_kind(may) == {
        "absence_deduction": Decimal("2158.26"),
        "sickness_inps_item": Decimal("1438.69"),
        "sickness_item": Decimal("370.93"),
    }
    (inputs,) = _decisions(may)
    assert inputs["chain_days"] == Decimal(147)
    assert "sickness_hospital_stay_not_modelled" in _codes(may)


def _august(start: date) -> PeriodResult:
    """Return August after sickness from 1 January to 2 June, imported.

    The imported episodes are complete from the hire date: no sick day of
    the employment is unknown.

    Returns:
        The August run with a six-day episode from ``start``.
    """
    opening = _ENGINE.import_opening_balances(
        OpeningBalances(
            tax_year=2026,
            payments=paid_before(PayrollRun.regular(2026, 8)),
            sickness_episodes=(
                SicknessEpisode("A", date(2026, 1, 1), date(2026, 6, 2)),
            ),
            sickness_known_from=_HIRED,
            inps_bases=(InpsBaseYtd(2026, other_employers=Decimal(0)),),
            recoveries=(),
            surtax_obligations=(),
        )
    )
    episode = SicknessEpisode("B", start, start.replace(day=start.day + 5))
    return _run(8, episode, opening=opening)


def _run(
    month: int, *episodes: SicknessEpisode, opening: PeriodState | None = None
) -> PeriodResult:
    period = PeriodInput(
        run=PayrollRun.regular(2026, month),
        payment_date=date(2026, month, 27),
        employment=_EMPLOYMENT,
        employer=_EMPLOYER,
        facts=PeriodFacts(events=episodes),
    )
    if opening is not None:
        period = replace(period, opening_state=opening)
    return _ENGINE.calculate_period(period)


@pytest.mark.parametrize(
    ("start", "chain", "rate"),
    [(date(2026, 8, 2), 159, "0.80"), (date(2026, 8, 3), 6, "1")],
    ids=["60_days_of_work", "61_days_of_work"],
)
def test_the_treatment_restarts_after_61_days_of_work(
    start: date, chain: int, rate: str
) -> None:
    """Back at work on 3 June after 31 + 28 + 31 + 30 + 31 + 2 = 153 days.

    3 June to 1 August are 60 days of work: a six-day episode from 2 August
    continues the chain at days 154-159, past 122, at 80%.  From 3 August,
    after 61 days, the treatment restarts: days 1-6 in full.  The three
    years hold 153 + 6 = 159 days, within the 183 of the comporto.
    """
    august = _august(start)
    (inputs,) = _decisions(august)
    assert inputs["chain_days"] == Decimal(chain)
    segments = str(inputs["segments"]).split(";")
    assert all(s.endswith(f":worker={rate}") for s in segments)
    assert "sickness_history_unknown" not in _codes(august)
    assert august.closing_state.accrual.sickness_known_from == _HIRED


def test_an_import_without_the_known_history_blocks() -> None:
    """Imported episodes of 2026 only, for a worker hired before 2026.

    The sickness of 2023-2025 could pass the comporto: the run names the
    fact to state.  Hired on 1 January 2026, nothing before is unknown.
    """
    balances = OpeningBalances(
        tax_year=2026,
        payments=paid_before(PayrollRun.regular(2026, 3)),
        inps_bases=(InpsBaseYtd(2026, other_employers=Decimal(0)),),
        recoveries=(),
        surtax_obligations=(),
    )
    episode = SicknessEpisode("M", date(2026, 3, 2), date(2026, 3, 13))
    unknown = _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                contract_type=Permanent(),
                ccnl_slug="metalmeccanico-federmeccanica.json",
                level_code="C3",
                category=WorkerCategory.OPERAIO,
                seniority=new_hire(2025),
            ),
            employer=_EMPLOYER,
            facts=PeriodFacts(events=(episode,)),
            opening_state=_ENGINE.import_opening_balances(balances),
        )
    )
    (issue,) = (i for i in unknown.issues if i.code == "sickness_history_unknown")
    assert issue.fact == "sickness_known_from"
    assert BlockerCode.MISSING_FACT in {b.code for b in unknown.blockers}
    hired = _run(3, episode, opening=_ENGINE.import_opening_balances(balances))
    assert "sickness_history_unknown" not in _codes(hired)


def _short(day: int, exempt: bool | None) -> SicknessEpisode:
    return SicknessEpisode(
        f"S{day}",
        date(2026, 3, day),
        date(2026, 3, day + 1),
        short_absence_exempt=exempt,
    )


def test_the_fourth_short_absence_of_the_year_is_paid_66_percent() -> None:
    """Two-day absences from Mondays 2, 9, 16 and 23 March 2026.

    Each is a new episode: days 1-2 are INPS waiting days the CCNL pays.
    By 26 each holds 2 days; the fourth is the 7th and 8th of the month:
    2158.26 * 8 / 26 = 664.08 less 2158.26 * 6 / 26 = 498.06, 166.02,
    paid 166.02 * 0.66 = 109.57.  The first three are paid 166.02 each.
    """
    march = _run(3, *(_short(day, False) for day in (2, 9, 16, 23)))
    paid = {
        i.item_id.rsplit("_", 2)[-2]: i.amount
        for i in march.pay_items
        if i.item_id.endswith("_crnz")
    }
    assert paid == {
        "evt0": Decimal("166.02"),
        "evt1": Decimal("166.02"),
        "evt2": Decimal("166.02"),
        "evt3": Decimal("109.57"),
    }
    assert "sickness_short_absence_exemption_unknown" not in _codes(march)


def test_an_unstated_exemption_pays_in_full_and_blocks() -> None:
    """The fourth absence without its exemption stated: 166.02, blocked."""
    march = _run(
        3, _short(2, False), _short(9, False), _short(16, False), _short(23, None)
    )
    fourth = next(i for i in march.pay_items if i.item_id.endswith("evt3_crnz"))
    assert fourth.amount == Decimal("166.02")
    (issue,) = (
        i for i in march.issues if i.code == "sickness_short_absence_exemption_unknown"
    )
    assert issue.fact == "short_absence_exempt"
    assert not march.is_payable
