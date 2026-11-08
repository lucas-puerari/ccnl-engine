"""Marittimi personale di terra: superminimi by years in the level.

Allegato 1 nn. 2-5 of the Sezione of 11 July 2024 (PDF p. 32): 7 EUR in
level IV after 8 years; 7 EUR in level III after 4 years with a diploma, or
after 8 years, never both; 11 EUR in level II after 10 years for a worker
without a further promotion.  The years in the level are
``SeniorityFact.career_months``.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import Employment
from ccnl_engine.inputs import NoPensionFund, Permanent, SeniorityFact, SenioritySource
from tests.knowledge.ccnl_engine.support import regular_period


def _superminimi(
    level: str, career: int, roles: frozenset[str] | None = None
) -> list[tuple[str, Decimal]]:
    seniority = SeniorityFact(
        150, date(2026, 1, 1), SenioritySource.EMPLOYER_RECORDS, career_months=career
    )
    employment = Employment(
        ccnl_id="marittimi-industria-armatoriale",
        level_code=level,
        seniority=seniority,
        pension_fund=NoPensionFund(),
        contract_type=Permanent(),
        roles=roles,
    )
    result = regular_period(employment=employment)
    return [
        (i.item_id.removeprefix("allowance_").split("_2026")[0], i.amount)
        for i in result.pay_items
        if "SUPERMINIMO" in i.item_id
    ]


_DIPLOMA = frozenset({"diplomato"})
_NO_PROMOTION = frozenset({"senza_passaggio"})


@pytest.mark.parametrize(
    ("level", "career", "roles", "expected"),
    [
        ("IV", 96, None, [("SUPERMINIMO_LIVELLO", Decimal("7.00"))]),
        ("IV", 95, None, []),
        ("III", 48, _DIPLOMA, [("SUPERMINIMO_LIVELLO_DIPLOMA", Decimal("7.00"))]),
        ("III", 96, _DIPLOMA, [("SUPERMINIMO_LIVELLO", Decimal("7.00"))]),
        ("III", 48, None, []),
        ("II", 120, _NO_PROMOTION, [("SUPERMINIMO_LIVELLO", Decimal("11.00"))]),
        ("II", 120, None, []),
    ],
    ids=[
        "iv-8-years",
        "iv-short",
        "iii-diploma-4-years",
        "iii-diploma-8-years-not-twice",
        "iii-no-diploma-4-years",
        "ii-no-promotion",
        "ii-promotion-foreseen",
    ],
)
def test_the_superminimo_of_the_years_in_the_level(
    level: str,
    career: int,
    roles: frozenset[str] | None,
    expected: list[tuple[str, Decimal]],
) -> None:
    """Paid from the years in the level, with the role the item names."""
    assert _superminimi(level, career, roles) == expected
