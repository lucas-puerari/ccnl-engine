"""A pay chain drops the seniority from an excluded extra month and a cohort allowance.

- Pubblici Esercizi FIPE art. 184 c. 1: the quattordicesima is due "esclusi
  [...] gli scatti di anzianità maturati"; the tredicesima includes them.
- Logistica Confetra art. 60 c. 8: an EDR for the workers "in servizio alla
  data del 26 gennaio 2011".
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.agreement.validity.rules import TimeSeries, ValidityPeriod
from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.compensation.models import Allowance

_SERIES = TimeSeries(
    periods=(
        ValidityPeriod(
            value=Decimal(10), valid_from=date(2025, 1, 1), valid_until=None
        ),
    )
)
_EDR = Allowance(
    code="EDR_2011", description="edr", monthly=_SERIES, in_service_on=date(2011, 1, 26)
)
_CHAIN = MonthlyPayChain(
    base=Decimal(1500),
    seniority=Decimal(80),
    allowances=((_EDR, Decimal(10)),),
    seniority_excluded_from=frozenset({14}),
)


def test_quattordicesima_leaves_out_the_seniority() -> None:
    """14 drops the 80 of seniority; 13 keeps it."""
    assert _CHAIN.for_extra_month(14).seniority == Decimal(0)
    assert _CHAIN.for_extra_month(13).seniority == Decimal(80)
    assert _CHAIN.scaled(Decimal("0.5")).seniority_excluded_from == frozenset({14})


@pytest.mark.parametrize(
    ("hired_on", "kept"),
    [(date(2011, 1, 26), True), (date(2011, 1, 27), False), (None, False)],
)
def test_cohort_allowance_needs_the_hire_date(
    hired_on: date | None, kept: bool
) -> None:
    """In service on 26 January 2011: hired that day or earlier."""
    chain = _CHAIN.for_hire_date(hired_on)

    assert (chain.allowances_total == Decimal(10)) is kept
    assert chain.seniority_excluded_from == frozenset({14})


def test_chain_without_cohort_allowances_is_kept() -> None:
    """Nothing to drop: the same chain comes back."""
    chain = MonthlyPayChain(base=Decimal(1), seniority=Decimal(0), allowances=())

    assert chain.for_hire_date(None) is chain
