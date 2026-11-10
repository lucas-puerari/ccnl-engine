"""Regression checks for sourced functional seniority allowance bands."""

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.element.rules import _level_chain


@pytest.mark.parametrize(
    ("service_months", "allowance", "monthly_total"),
    [
        (192, Decimal("0.00"), Decimal("1714.70")),
        (204, Decimal("121.53"), Decimal("1836.23")),
        (324, Decimal("245.82"), Decimal("1960.52")),
        (384, Decimal("282.69"), Decimal("1997.39")),
    ],
)
def test_agent_functional_allowance_bands(
    service_months: int, allowance: Decimal, monthly_total: Decimal
) -> None:
    """Agent: 1458.40/12=121.53 at 17y, 2949.83/12=245.82 at 27y.

    At 32y, 3392.30/12=282.69. Before 17y the allowance is zero.
    """
    ccnl = load_ccnl("forze-polizia-ordinamento-civile")
    level = ccnl.level_by_code("AGENTE")
    chain = _level_chain(
        ccnl,
        level,
        0,
        frozenset(),
        date(2026, 1, 1),
        is_apprentice=False,
        seniority_months=service_months,
    )
    assert chain.base == Decimal("1714.70")
    assert sum((value for _, value in chain.allowances), Decimal(0)) == allowance
    assert chain.base + chain.seniority + allowance == monthly_total
    extra = chain.for_extra_month(13)
    assert sum((value for _, value in extra.allowances), Decimal(0)) == allowance
    assert all(item.months_per_year == 13 for item, _ in chain.allowances)
    assert len(chain.allowances) == (0 if service_months < 204 else 1)


def test_commissioner_requires_lower_rank_origin() -> None:
    """Vice commissioner from lower ranks: 2153.50/12 = 179.46 at 17 years.

    Without lower-rank origin, the allowance is zero.
    """
    ccnl = load_ccnl("forze-polizia-ordinamento-civile")
    level = ccnl.level_by_code("VICE_COMM")
    for roles, expected in (
        (frozenset(), Decimal("0.00")),
        (frozenset({"promoted_from_lower_rank"}), Decimal("179.46")),
    ):
        chain = _level_chain(
            ccnl,
            level,
            0,
            roles,
            date(2026, 1, 1),
            is_apprentice=False,
            seniority_months=204,
        )
        assert sum((value for _, value in chain.allowances), Decimal(0)) == expected
