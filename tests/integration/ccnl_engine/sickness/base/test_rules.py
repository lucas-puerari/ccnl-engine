"""A sickness episode across two months, on the INPS base of the month before.

Metalmeccanico Federmeccanica C3 operaio, hired in 2025: 2158.26 EUR a month
to 31 May 2026 and 2211.43 from 1 June.  The episode runs from Monday 25 May
to Wednesday 10 June 2026.  April 2026 is the month before it: pay
(retribuzione teorica) 2158.26 over 26 days worked or paid, 13 monthly
payments.  Computed by hand from INPS circ. 134368/1981 point 11.3:

- RMGG = 2158.26 / 26 + (2158.26 * 1 / 12) / 25 = 83.01 + 7.1942 = 90.2042;
- days 1-3 (25-27 May) carenza, INPS pays nothing;
- days 4-7 (28-31 May, four calendar days, Sunday included) at 50%:
  4 * 0.5 * 90.2042 = 180.4084 -> 180.41;
- days 8-17 (1-10 June, ten calendar days) at 50%: 10 * 0.5 * 90.2042 =
  451.021 -> 451.02, still on the April base although June pays 2211.43.

The CCNL pays the first 122 days of the chain in full: the employer tops the
INPS share up to the daily pay the run deducts, on the June pay in June.
May deducts 2158.26 * 6 / 26 = 498.06 (three carenza and three indemnified
payable days, by 26), pays the carenza 249.03 and tops up 249.03 - 180.41 =
68.62.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine import (
    Employment,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.inputs import FixedTerm, NaspiExclusion, Permanent
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId
from ccnl_engine.sickness.base.inputs import InpsSicknessBase, SpettacoloSicknessBase
from ccnl_engine.sickness.models import SicknessEpisode
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult

_APRIL = InpsSicknessBase(Decimal("2158.26"), Decimal(0), paid_days=26)
_EPISODE = SicknessEpisode("S1", date(2026, 5, 25), date(2026, 6, 10), inps_base=_APRIL)
_RMGG = Decimal("2158.26") / 26 + Decimal("2158.26") / 12 / 25


def _run(month: int, episode: SicknessEpisode, opening: PeriodState) -> PeriodResult:
    request = PeriodCalculationRequest(
        employer=EmployerProfile(headcount=Headcount(50)),
        period_id=PeriodId(year=2026, month=month),
        payment_date=date(2026, month, 27),
        ccnl_id="metalmeccanico-federmeccanica",
        level_code="C3",
        seniority=new_hire(2025),
        opening_state=opening,
        events=(episode,),
        category=WorkerCategory.OPERAIO,
    )
    return calculate_period(
        request, repo=bundled_repository(), resolver=bundled_policies()
    )


def _sick(result: PeriodResult) -> dict[str, Decimal]:
    return {
        item.item_id.rsplit("_", 1)[1]: item.amount
        for item in result.pay_items
        if "_evt" in item.item_id
    }


def test_may_pays_the_inps_share_on_the_april_base() -> None:
    """Four calendar days at 50% of the RMGG; the employer tops up the rest."""
    may = _run(5, _EPISODE, PeriodState.zero())

    assert _sick(may) == {
        "abs": Decimal("498.06"),
        "inps": Decimal("180.41"),
        "intg": Decimal("68.62"),
        "crnz": Decimal("249.03"),
    }
    assert "sickness_inps_base_unknown" not in {i.code for i in may.issues}
    (decision,) = (d for d in may.decisions if d.capability == "sickness")
    assert decision.inputs["inps_daily_base"] == _RMGG


def test_june_keeps_the_april_base_through_the_pay_rise() -> None:
    """Ten calendar days on the April base; the top-up follows the June pay."""
    may = _run(5, _EPISODE, PeriodState.zero())
    june = _run(6, _EPISODE, may.closing_state)

    sick = _sick(june)
    assert sick["inps"] == Decimal("451.02")
    assert sick["inps"] + sick["intg"] == sick["abs"]
    assert sick["abs"] > Decimal("2158.26") * 9 / 26
    assert "sickness_inps_base_unknown" not in {i.code for i in june.issues}


def test_a_relapse_takes_the_base_of_the_episode_it_continues() -> None:
    """A relapse in June states no base: INPS pays it on the April one."""
    first = SicknessEpisode(
        "S1", date(2026, 5, 25), date(2026, 5, 31), inps_base=_APRIL
    )
    may = _run(5, first, PeriodState.zero())
    relapse = SicknessEpisode(
        "S1-R", date(2026, 6, 8), date(2026, 6, 10), relapse_of="S1"
    )
    june = _run(6, relapse, may.closing_state)

    (decision,) = (d for d in june.decisions if d.capability == "sickness")
    assert decision.inputs["inps_daily_base"] == _RMGG
    # Days 8-10 of the chain at 50%: 3 * 0.5 * 90.2042 = 135.3063 -> 135.31.
    assert _sick(june)["inps"] == Decimal("135.31")


def test_without_the_base_the_share_stays_on_the_quota_and_blocks() -> None:
    """No pay of the month before: a missing fact blocks the run."""
    episode = SicknessEpisode("S1", date(2026, 5, 25), date(2026, 6, 10))
    may = _run(5, episode, PeriodState.zero())

    assert ("missing_fact", "inps_base") in {(b.code, b.detail) for b in may.blockers}
    (decision,) = (d for d in may.decisions if d.capability == "sickness")
    assert decision.inputs["inps_daily_base"] == "none"


def _cinema(
    base: InpsSicknessBase | SpettacoloSicknessBase, *, fixed_term: bool
) -> PeriodResult:
    """Return March 2026 of a film production impiegato sick from 2 to 11 March.

    Returns:
        The result of the run.
    """
    contract: FixedTerm | Permanent = (
        FixedTerm(renewals=0, naspi_exclusion=NaspiExclusion.NONE)
        if fixed_term
        else Permanent()
    )
    episode = SicknessEpisode(
        "CIN",
        date(2026, 3, 2),
        date(2026, 3, 11),
        daily_contributions=120,
        prior_worked_days=200 if fixed_term else None,
        inps_base=base,
    )
    request = PeriodInput(
        run=PayrollRun.regular(2026, 3),
        payment_date=date(2026, 3, 27),
        employment=Employment(
            ccnl_id="cinema-audiovisivi-industria",
            level_code="4",
            category=WorkerCategory.IMPIEGATO,
            contract_type=contract,
            seniority=new_hire(2025),
        ),
        employer=EmployerProfile(headcount=Headcount(50)),
        facts=PeriodFacts(events=(episode,)),
    )
    return PayrollEngine.bundled().calculate_period(request)


def _base_of(result: PeriodResult) -> object:
    (decision,) = (d for d in result.decisions if d.capability == "sickness")
    return decision.inputs["inps_daily_base"]


def test_spettacolo_averages_the_last_daily_contributions() -> None:
    """4000 EUR over 40 contributions: 100 a day (circ. 132/2021 par. 2.4)."""
    result = _cinema(SpettacoloSicknessBase(Decimal(4000), 40), fixed_term=False)

    assert _base_of(result) == Decimal(100)
    assert "sickness_inps_base_unknown" not in {i.code for i in result.issues}


def test_a_fixed_term_spettacolo_base_stops_at_the_ceiling() -> None:
    """6000 / 40 = 150 a day, capped at the 100 EUR of art. 66 c. 3 D.L. 73/2021."""
    result = _cinema(SpettacoloSicknessBase(Decimal(6000), 40), fixed_term=True)

    assert _base_of(result) == Decimal(100)


def test_spettacolo_does_not_read_the_month_before() -> None:
    """The general base does not stand for the spettacolo one."""
    result = _cinema(InpsSicknessBase(Decimal(2000), Decimal(0)), fixed_term=False)

    assert _base_of(result) == "none"
