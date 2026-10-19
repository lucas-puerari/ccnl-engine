"""The minimi of the CCNL of the cooperative e consorzi agricoli.

Signed verbale of 19 July 2024 (FLAI CGIL, sha256
67f866fda39e80945ddd67ba6a59c1489f419fce02f0ba2c771a237ade68a616), read on
14 October 2026: All. n. 1, "Tabella minimi retributivi nazionali conglobati
mensili" (p. 19).  Every level at each of the four tranches, the day before
each later one still paying the tranche before; the fixed-term operai and
the operai past their fifth scatto are declared limitations.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl

_CCNL = load_ccnl("cooperative-consorzi-agricoli")
_TRANCHES = (date(2024, 4, 1), date(2025, 5, 1), date(2026, 5, 1), date(2027, 2, 1))
_TABLE = (
    ("1", ("2200.92", "2235.08", "2269.24", "2303.40")),
    ("2", ("1978.64", "2009.35", "2040.06", "2070.77")),
    ("3", ("1821.25", "1849.52", "1877.79", "1906.06")),
    ("4", ("1693.44", "1719.73", "1746.02", "1772.31")),
    ("5", ("1610.38", "1635.38", "1660.38", "1685.38")),
    ("6", ("1563.74", "1588.01", "1612.28", "1636.55")),
    ("7", ("1450.84", "1473.36", "1495.88", "1518.40")),
    ("np", ("1223.82", "1242.82", "1261.82", "1280.82")),
)


@pytest.mark.parametrize(("level", "amounts"), _TABLE)
def test_each_tranche_of_the_table(level: str, amounts: tuple[str, ...]) -> None:
    """The printed minimo conglobato from each tranche."""
    salary = _CCNL.level_by_code(level).base_salary
    values = [Decimal(a) for a in amounts]

    for start, value in zip(_TRANCHES, values, strict=True):
        assert salary.value_at(start) == value
    for start, previous in zip(_TRANCHES[1:], values, strict=False):
        assert salary.value_at(start - timedelta(days=1)) == previous


def test_operai_gaps_are_declared() -> None:
    """The terzo elemento and the operai scatti block the runs they concern."""
    scopes = {
        note.limitation.variant: note.limitation.applies_when
        for note in _CCNL.coverage.notes
        if note.limitation is not None
    }
    otd = scopes["otd_terzo_elemento_missing"]
    seniority = scopes["operai_seniority_over_five"]

    assert otd.contract_types == frozenset({"fixed_term"})
    assert otd.worker_categories == frozenset({"operaio"})
    assert seniority.seniority_months_from == 144
