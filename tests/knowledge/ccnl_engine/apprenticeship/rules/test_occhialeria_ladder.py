"""Occhialeria art. 24: the apprentice is paid two levels below, then one.

CCNL of 10 June 2021, pp. 39-40 (table in force from 1 July 2017): "nel
primo periodo di apprendistato professionalizzante: due livelli sotto
quello di destinazione finale; nel secondo periodo: un livello sotto [...];
nel terzo e ultimo periodo: livello di destinazione finale", over 10, 10
and 16 months; a 2nd-level apprentice is at the destination "dall'inizio
del secondo periodo" (6 months).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ccnl_engine import Employment, PeriodResult
from ccnl_engine.inputs import Apprentice, Permanent
from tests.knowledge.ccnl_engine.support import regular_period

if TYPE_CHECKING:
    from decimal import Decimal

pytestmark = pytest.mark.legal_scenario

_SLUG = "occhiali-occhialeria-industria"


def _base_salary(result: PeriodResult) -> Decimal:
    (item,) = (i for i in result.pay_items if i.kind == "base_salary_earning")
    return item.amount


def _run(level: str, months_elapsed: int | None) -> Decimal:
    contract = (
        Permanent()
        if months_elapsed is None
        else Apprentice(months_elapsed=months_elapsed)
    )
    return _base_salary(
        regular_period(
            month=3,
            employment=Employment(
                ccnl_id=_SLUG, level_code=level, contract_type=contract
            ),
        )
    )


@pytest.mark.parametrize(
    ("destination", "months_elapsed", "paid_as"),
    [
        ("4S", 0, "3S"),
        ("4S", 10, "4"),
        ("4S", 20, "4S"),
        ("2", 0, "1"),
        ("2", 6, "2"),
    ],
)
def test_the_apprentice_is_paid_at_the_level_of_the_period(
    destination: str, months_elapsed: int, paid_as: str
) -> None:
    """The base salary is the full one of the level the period names."""
    assert _run(destination, months_elapsed) == _run(paid_as, None)
