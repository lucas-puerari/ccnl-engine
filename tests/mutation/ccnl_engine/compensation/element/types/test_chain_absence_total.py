"""The absence quota leaves out an allowance with no incidence on institutes.

CCNL Logistica, renewal of 18 May 2021 (CNEL deposit 136045, PDF p. 3):
"L'EDR di 10 euro lordi [...] non avrà incidenza su alcun istituto
contrattuale".  The EDR stays in cash pay but out of the daily quota an
absence deducts and a sickness tops up.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.agreement.validity.rules import TimeSeries, ValidityPeriod
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.compensation.models import Allowance

_SERIES = TimeSeries(
    periods=(
        ValidityPeriod(value=Decimal(1), valid_from=date(2025, 1, 1), valid_until=None),
    )
)
_EDR = Allowance(
    code="EDR_2021", description="edr", monthly=_SERIES, absence_relevant=False
)
_CASH = Allowance(code="cash", description="cash", monthly=_SERIES)
_BOARD = Allowance(code="board", description="board", monthly=_SERIES, in_kind=True)
_CHAIN = MonthlyPayChain(
    base=Decimal(2000),
    seniority=Decimal(0),
    allowances=(
        (_CASH, Decimal("20.00")),
        (_EDR, Decimal("9.70")),
        (_BOARD, Decimal("100.00")),
    ),
)


def test_absence_total_leaves_out_edr_and_in_kind() -> None:
    """Cash 29.70, of which 20.00 counts for the absence quota."""
    assert _CHAIN.allowances_total == Decimal("29.70")
    assert _CHAIN.absence_total == Decimal("20.00")
    assert _CASH.absence_relevant


def test_prorated_absence_total() -> None:
    """Half the month: 10.00 of the counted allowance."""
    half = _CHAIN.prorated(Decimal(13), Decimal(26))
    assert half.absence_total == Decimal("10.00")


def test_logistica_edr_2021_is_out_of_the_absence_quota() -> None:
    """Every EDR_2021 of both Logistica files has absence_relevant false."""
    for slug in (
        "logistica-trasporto-confetra",
        "logistica-trasporto-confetra-viaggiante",
    ):
        flags = {
            a.absence_relevant
            for level in load_ccnl(slug).levels
            for a in level.fixed_allowances
            if a.code == "EDR_2021"
        }
        assert flags == {False}, slug
