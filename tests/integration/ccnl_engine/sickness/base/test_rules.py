"""P06: a sickness episode across two months, on the INPS base of the month before.

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

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId
from ccnl_engine.sickness.base.inputs import InpsSicknessBase
from ccnl_engine.sickness.models import SicknessEpisode
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult

_APRIL = InpsSicknessBase(Decimal("2158.26"), Decimal(0), paid_days=26)
_EPISODE = SicknessEpisode(
    "P06", date(2026, 5, 25), date(2026, 6, 10), inps_base=_APRIL
)
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
    assert "sickness_inps_daily_base" not in {lim.id for lim in may.limitations}
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
    assert "sickness_inps_daily_base" not in {lim.id for lim in june.limitations}


def test_a_relapse_takes_the_base_of_the_episode_it_continues() -> None:
    """A relapse in June states no base: INPS pays it on the April one."""
    first = SicknessEpisode(
        "P06", date(2026, 5, 25), date(2026, 5, 31), inps_base=_APRIL
    )
    may = _run(5, first, PeriodState.zero())
    relapse = SicknessEpisode(
        "P06-R", date(2026, 6, 8), date(2026, 6, 10), relapse_of="P06"
    )
    june = _run(6, relapse, may.closing_state)

    (decision,) = (d for d in june.decisions if d.capability == "sickness")
    assert decision.inputs["inps_daily_base"] == _RMGG
    # Days 8-10 of the chain at 50%: 3 * 0.5 * 90.2042 = 135.3063 -> 135.31.
    assert _sick(june)["inps"] == Decimal("135.31")


def test_without_the_base_the_share_stays_on_the_quota_and_blocks() -> None:
    """No pay of the month before: the limitation still applies."""
    episode = SicknessEpisode("P06", date(2026, 5, 25), date(2026, 6, 10))
    may = _run(5, episode, PeriodState.zero())

    assert "sickness_inps_daily_base" in {lim.id for lim in may.limitations}
    (decision,) = (d for d in may.decisions if d.capability == "sickness")
    assert decision.inputs["inps_daily_base"] == "none"
