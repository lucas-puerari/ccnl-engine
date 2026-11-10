"""Federlegno third-period midpoint with split tabular pay."""

from datetime import date
from decimal import Decimal

from ccnl_engine.apprenticeship.rules import _apprentice_chain
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employment.inputs import Apprentice


def test_ae3_to_ae4_third_period_averages_all_tabular_components() -> None:
    """September 2026: (AE3 2161.48 + AE4 2257.04) / 2 = EUR 2209.26.

    AE3: 1634.62 + 516.53 + 10.33; AE4: 1728.95 + 517.76 + 10.33.
    Contingenza averages to 517.15; EDR stays 10.33. Classification
    remains AE3 rather than moving early to AE4.
    """
    ccnl = load_ccnl("legno-arredamento-federlegno")
    chain, percentage, pay_level = _apprentice_chain(
        ccnl,
        ccnl.level_by_code("AE4"),
        Apprentice(months_elapsed=30),
        count=1,
        roles=frozenset(),
        as_of=date(2026, 9, 1),
    )
    assert pay_level == "AE3"
    assert percentage is None
    assert chain.base + chain.allowances_total == Decimal("2209.26")
    assert {allowance.code: amount for allowance, amount in chain.allowances} == {
        "CONTINGENZA": Decimal("517.15"),
        "EDR": Decimal("10.33"),
    }
    assert "legno-arredamento-federlegno/apprenticeship_midpoint_components" not in (
        chain.limitations
    )
