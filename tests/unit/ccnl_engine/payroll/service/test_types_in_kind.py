"""A pay chain keeps a benefit provided in kind out of cash until the extra month.

CCNL lavoro domestico of 28 October 2025: the board and lodging of a live-in
worker are provided in kind (art. 36), enter the TFR base at their
conventional value (art. 41 c. 1) and are paid in cash in the tredicesima
(art. 39 c. 1, chiarimento a verbale 5).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.domain.compensation import Allowance
from ccnl_engine.contract.domain.validity import TimeSeries, ValidityPeriod
from ccnl_engine.payroll.service.types import MonthlyPayChain

_SERIES = TimeSeries(
    periods=(
        ValidityPeriod(value=Decimal(1), valid_from=date(2026, 1, 1), valid_until=None),
    )
)
_BOARD = Allowance(
    code="vitto_alloggio", description="board", monthly=_SERIES, in_kind=True
)
_CASH = Allowance(code="cash", description="cash", monthly=_SERIES)
_CHAIN = MonthlyPayChain(
    base=Decimal("1193.84"),
    seniority=Decimal(0),
    allowances=((_CASH, Decimal(10)), (_BOARD, Decimal("199.80"))),
)


def test_in_kind_allowance_is_not_cash() -> None:
    """The cash total leaves the board out; the in-kind total holds it."""
    assert _CHAIN.allowances_total == Decimal(10)
    assert _CHAIN.in_kind_total == Decimal("199.80")


def test_extra_month_pays_the_in_kind_allowance_in_cash() -> None:
    """The tredicesima pays 10 + 199.80 in cash and nothing in kind."""
    extra = _CHAIN.for_extra_month(13)

    assert extra.allowances_total == Decimal("209.80")
    assert extra.in_kind_total == Decimal(0)
    assert [a.code for a, _ in extra.allowances] == ["cash", "vitto_alloggio"]
    assert _BOARD.in_kind


def test_part_time_keeps_an_unproportionable_in_kind_value() -> None:
    """Art. 14 c. 2: board and lodging are owed in full at reduced hours."""
    board = _BOARD.model_copy(update={"part_time_proportionable": False})
    chain = MonthlyPayChain(
        base=Decimal(1000),
        seniority=Decimal(0),
        allowances=((board, Decimal("199.80")),),
    )

    half = chain.scaled_for_part_time(Decimal("0.5"))

    assert (half.base, half.in_kind_total) == (Decimal(500), Decimal("199.80"))
