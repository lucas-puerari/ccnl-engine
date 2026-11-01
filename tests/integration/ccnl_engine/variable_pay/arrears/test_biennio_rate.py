"""The rate of the separate taxation of arrears from the income of the biennio.

Art. 21 TUIR (Normattiva, text in force from 31-12-2024 to 31-12-2026,
page sha256 9638f2c5aec6e3615193a672b6d07c3cd31083640b1c890b73022aa9951745f1):
c. 1, "l'aliquota corrispondente alla metà del reddito complessivo netto del
contribuente nel biennio anteriore all'anno in cui [...] sono percepiti"
for the arrears of art. 17 c. 1 lett. b; c. 3, a year without income takes
half the other's, two years without income the rate of the first bracket.

Arrears of June 2025 paid in March 2026, EUR 2,000.00.  Income 30,000 and
32,000: half 31,000, IRPEF 2026 28,000 x 23% + 3,000 x 33% = 7,430, rate
7,430 / 31,000, tax 2,000 x rate = 479.35.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.decision.models import (
    CalculationDecision,
    CalculationStatus,
    DecisionOrigin,
)
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.inputs import PeriodState, PriorYearTaxFacts
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId
from ccnl_engine.variable_pay.arrears.handlers import UNUSED_DEDUCTIONS
from ccnl_engine.variable_pay.inputs import ArrearsEvent

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult

_ARREARS = ArrearsEvent(
    date(2026, 3, 28), Decimal("2000.00"), reference_period=PeriodId(2025, 6)
)


def _run(
    biennio: tuple[Decimal, Decimal] | None, event: ArrearsEvent = _ARREARS
) -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_id="metalmeccanico-federmeccanica",
            level_code="C3",
            opening_state=PeriodState.zero(),
            events=(event,),
            prior_year=PriorYearTaxFacts(net_income_biennio=biennio),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )


def _separate(result: PeriodResult) -> Decimal:
    return sum(
        (
            e.amount
            for e in result.ledger_entries
            if e.account is AccountKind.SEPARATE_TAX
        ),
        Decimal(0),
    )


def _decision(result: PeriodResult) -> CalculationDecision:
    (decision,) = (
        d
        for d in result.decisions
        if d.capability == "contract_renewal_arrears"
        and d.origin is DecisionOrigin.ENGINE
    )
    return decision


@pytest.mark.parametrize(
    ("biennio", "rate"),
    [
        ((Decimal(30_000), Decimal(32_000)), Decimal(7430) / Decimal(31_000)),
        ((Decimal(0), Decimal(20_000)), Decimal("0.23")),
        ((Decimal(0), Decimal(0)), Decimal("0.23")),
    ],
)
def test_the_engine_rates_the_arrears_on_half_the_biennio(
    biennio: tuple[Decimal, Decimal], rate: Decimal
) -> None:
    """Half the income of the two years at the 2026 brackets."""
    result = _run(biennio)
    decision = _decision(result)
    tax = (Decimal("2000.00") * rate).quantize(Decimal("0.01"), ROUND_HALF_UP)

    assert _separate(result) == tax
    assert decision.status is CalculationStatus.FINAL
    assert (decision.inputs["separate_tax_rate"], decision.inputs["rate_source"]) == (
        rate,
        "biennio",
    )
    assert UNUSED_DEDUCTIONS in {lim.id for lim in result.limitations}


def test_thirty_and_thirty_two_thousand_tax_479_35() -> None:
    """The hand figure of the module docstring."""
    assert _separate(_run((Decimal(30_000), Decimal(32_000)))) == Decimal("479.35")


def test_a_caller_rate_prevails() -> None:
    """The caller's 23% whatever the biennio, with no limitation."""
    stated = replace(_ARREARS, separate_tax_rate=Decimal("0.23"))
    result = _run((Decimal(30_000), Decimal(32_000)), stated)

    assert _separate(result) == Decimal("460.00")
    assert _decision(result).inputs["rate_source"] == "caller"
    assert UNUSED_DEDUCTIONS not in {lim.id for lim in result.limitations}


def test_without_rate_or_biennio_the_separate_tax_is_open() -> None:
    """No separate tax, an incomplete decision and the fact to state."""
    result = _run(None)
    decision = _decision(result)

    assert _separate(result) == Decimal(0)
    assert (decision.status, decision.amount) == (CalculationStatus.INCOMPLETE, None)
    assert "net_income_biennio" in {i.fact for i in result.issues}


@pytest.mark.parametrize("biennio", [(Decimal(1),), (Decimal(-1), Decimal(1))])
def test_the_biennio_is_two_non_negative_amounts(
    biennio: tuple[Decimal, ...],
) -> None:
    """One amount, or a negative one, is rejected."""
    with pytest.raises(InvalidInputError, match="net_income_biennio"):
        PriorYearTaxFacts(net_income_biennio=biennio)  # type: ignore[arg-type]
