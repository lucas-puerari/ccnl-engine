"""INPS sickness regime of the lavoratori dello spettacolo (circ. 132/2021).

From the fourth day 60% up to the 20th day, 80% from the 21st to the 180th;
no additional contribution: the regime is funded by the ordinary rates.
"""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.catalog.loaders import load_ccnl
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
        "cinema-audiovisivi-industria.json",
        "esercizi-cinematografici-anec.json",
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
