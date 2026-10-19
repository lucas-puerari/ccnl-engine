"""INPS sickness regime of the lavoratori dello spettacolo (circ. 132/2021).

From the fourth day 60% up to the 20th day, 80% from the 21st to the 180th;
no additional contribution: the regime is funded by the ordinary rates.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.events import SicknessEpisode
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import calculate_period
from ccnl_engine.run.types import PeriodId
from ccnl_engine.sickness.indemnity.loaders import load_sick_pay_rates


def test_the_regime_bands() -> None:
    """60% on days 4-20, 80% on days 21-180."""
    rates = load_sick_pay_rates().for_regime("spettacolo")
    assert rates.band_rate(4) == Decimal("0.60")
    assert rates.band_rate(20) == Decimal("0.60")
    assert rates.band_rate(21) == Decimal("0.80")
    assert rates.band_rate(180) == Decimal("0.80")


def test_the_cinema_ccnls_name_it() -> None:
    """Film production and cinema exhibition staff are in the FPLS."""
    for slug in (
        "cinema-audiovisivi-industria",
        "esercizi-cinematografici-anec",
    ):
        work = load_ccnl(slug).work_rules
        assert work is not None
        assert work.sickness_rules is not None
        assert work.sickness_rules.inps_regime == "spettacolo"


def test_no_additional_contribution() -> None:
    """Unlike the pubblici esercizi, the regime has no supplement."""
    regimes = {r.id: r for r in load_sick_pay_rates().regimes}
    assert regimes["pubblici_esercizi"].additional_contribution
    assert not regimes["spettacolo"].additional_contribution


def _inps_share(contributions: int | None) -> Decimal:
    episode = SicknessEpisode(
        "CIN", date(2026, 3, 2), date(2026, 3, 11), daily_contributions=contributions
    )
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_id="cinema-audiovisivi-industria",
            level_code="4",
            category=WorkerCategory.IMPIEGATO,
            opening_state=PeriodState.zero(),
            events=(episode,),
        )
    )
    return sum(
        (i.amount for i in result.pay_items if i.kind == "sickness_inps_item"),
        Decimal(0),
    )


def test_an_impiegato_is_covered_with_40_contributions() -> None:
    """Impiegati of the FPLS are covered; under 40 contributions INPS pays nothing."""
    assert _inps_share(120) > 0
    assert _inps_share(39) == 0
