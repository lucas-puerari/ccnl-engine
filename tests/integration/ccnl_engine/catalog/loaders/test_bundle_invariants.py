"""Data-quality invariants over every bundled CCNL data file.

Each test checks one invariant on all the CCNLs at once and lists every
CCNL that breaks it.  Invariants the models enforce at load time (unique
level codes and orders, an open-ended last period, a recorded hash equal to
the computed one) are not repeated here: loading the bundle checks them.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.catalog.loaders import list_contracts, load_ccnl

if TYPE_CHECKING:
    from collections.abc import Iterator

    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.agreement.validity.rules import TimeSeries

_ALL_CCNL: list[CCNL] = [load_ccnl(ci.ccnl_id) for ci in list_contracts()]

# Salary table range: EUR 100-10000 per month.
_SALARY_MIN = Decimal(100)
_SALARY_MAX = Decimal(10000)
# Hourly divisor: valid Italian CCNL range 100-250 hours per month.
_DIVISOR_MIN = Decimal(100)
_DIVISOR_MAX = Decimal(250)
# Additional months: Italian CCNL always adds 1-4 extra months (13th-16th).
_MONTHS_MIN = Decimal(12)
_MONTHS_MAX = Decimal(16)


def _salary_series(ccnl: CCNL) -> Iterator[tuple[str, TimeSeries]]:
    for level in ccnl.levels:
        yield f"{ccnl.meta.ccnl_id}/{level.code}", level.base_salary


def _parameter_series(name: str) -> Iterator[tuple[str, TimeSeries]]:
    for ccnl in _ALL_CCNL:
        yield ccnl.meta.ccnl_id, getattr(ccnl.parameters, name)


def _gaps(series: Iterator[tuple[str, TimeSeries]]) -> list[str]:
    return [
        f"{where}: gap {p.gap_kind}"
        for where, s in series
        for p in s.periods
        if p.is_gap
    ]


def _outside(
    series: Iterator[tuple[str, TimeSeries]],
    low: Decimal,
    high: Decimal,
    *,
    inclusive: bool = True,
) -> list[str]:
    def within(value: Decimal) -> bool:
        return low <= value <= high if inclusive else low < value < high

    return [
        f"{where}: {p.value}"
        for where, s in series
        for p in s.periods
        if p.value is None or not within(p.value)
    ]


def test_the_bundle_holds_134_ccnls() -> None:
    """Exactly 134 CCNL data files are bundled."""
    assert len(_ALL_CCNL) == 134


def test_every_ruleset_identity_names_its_ccnl() -> None:
    """Every CCNL carries a ruleset identity whose id embeds its slug."""
    wrong = [
        c.meta.ccnl_id
        for c in _ALL_CCNL
        if c.ruleset is None or c.meta.ccnl_id not in c.ruleset.id
    ]
    assert wrong == []


def test_no_base_salary_has_a_gap() -> None:
    """No base salary period of any level is a gap period."""
    assert _gaps(s for c in _ALL_CCNL for s in _salary_series(c)) == []


def test_every_base_salary_is_within_range() -> None:
    """Every base salary is within 100-10000 EUR a month."""
    series = (s for c in _ALL_CCNL for s in _salary_series(c))
    assert _outside(series, _SALARY_MIN, _SALARY_MAX) == []


def test_no_parameter_has_a_gap() -> None:
    """The hourly divisor and the additional months have no gap period."""
    assert _gaps(_parameter_series("hourly_divisor")) == []
    assert _gaps(_parameter_series("additional_months")) == []


def test_every_parameter_is_within_range() -> None:
    """Hourly divisor strictly within 100-250 hours, 12 to 16 monthly payments."""
    divisors = _parameter_series("hourly_divisor")
    months = _parameter_series("additional_months")
    assert _outside(divisors, _DIVISOR_MIN, _DIVISOR_MAX, inclusive=False) == []
    assert _outside(months, _MONTHS_MIN, _MONTHS_MAX) == []
