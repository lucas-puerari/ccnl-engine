"""Tax year attribution and obligations that survive the year change."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import (
    Employment,
    OpeningBalances,
    PayrollEngine,
    PayrollRun,
    PayrollState,
    PeriodInput,
    RecoveryObligation,
    RecoveryPlan,
)
from ccnl_engine.engine.errors import InvalidInputError, UnsupportedTaxYearError
from ccnl_engine.payroll.domain.employment_context import TemporalContext
from ccnl_engine.payroll.domain.tax_year_state import TaxYearState
from tests.acceptance.legal_scenarios._support import (
    COMMERCIO,
    EMPLOYER,
    ENGINE,
    regular_period,
)
from tests.fixtures.next_year_repository import NextYearRepository

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult

pytestmark = pytest.mark.legal_scenario


def test_december_paid_by_twelve_january_stays_in_previous_year() -> None:
    """Cassa allargata: pay paid by 12 January belongs to the previous year.

    Art. 51 c. 1 TUIR: December 2026 pay paid on 12 January 2027 is 2026 income.
    """
    result = regular_period(month=12, payment_date=date(2027, 1, 12))

    assert result.closing_state.tax_year == 2026


def test_december_paid_by_ten_january_stays_in_previous_year() -> None:
    """Art. 51 c. 1 TUIR: December 2026 paid on 10 January 2027 is 2026 income."""
    result = regular_period(month=12, payment_date=date(2027, 1, 10))

    assert result.closing_state.tax_year == 2026


def test_december_paid_after_twelve_january_moves_to_next_year() -> None:
    """Art. 51 c. 1 TUIR: pay received after 12 January is taxed by cash in 2027."""
    temporal = TemporalContext.from_period(2026, 12, date(2027, 1, 13))

    assert temporal.competence == date(2026, 12, 1)
    assert temporal.fiscal_year == 2027


@pytest.mark.parametrize(
    ("payment_date", "tax_year"),
    [(date(2027, 1, 13), 2027), (date(2028, 6, 28), 2028)],
)
def test_run_of_unbundled_tax_year_raises_domain_error(
    payment_date: date, tax_year: int
) -> None:
    """The engine computes the run with the payment year's tables.

    Those tables are not bundled, so the run fails with a domain error that
    names the attributed tax year instead of computing it with 2026 rules.
    """
    with pytest.raises(UnsupportedTaxYearError) as info:
        regular_period(month=12, payment_date=payment_date)

    assert info.value.year == tax_year


def test_run_of_next_tax_year_is_not_added_to_current_year_state() -> None:
    """December 2026 paid on 13 January 2027 cannot close into the 2026 state."""
    opening = PayrollState(
        ytd=TaxYearState(
            tax_year=2026, regular_periods_closed=11, tax_withholding_periods_closed=11
        )
    )

    with pytest.raises(InvalidInputError, match="belongs to tax year 2027"):
        regular_period(month=12, payment_date=date(2027, 1, 13), opening_state=opening)


_PLAN = RecoveryPlan(
    kind="trattamento_integrativo",
    original_amount=Decimal(160),
    installment_amount=Decimal(20),
    installments_total=8,
    installments_posted=2,
)
_NEXT_YEAR_ENGINE = PayrollEngine(repository=NextYearRepository())


def _december_2026() -> tuple[PeriodResult, PeriodResult]:
    """Close 2026 on Commercio L4: December, then the tredicesima.

    The opening balances come from a previous provider: 11 regular runs and
    the quattordicesima paid, 160.00 of trattamento integrativo recognized
    and a recovery plan of 8 x 20.00 with 2 installments posted (40.00).

    Returns:
        The December and tredicesima results, in payment order.
    """
    opening = OpeningBalances(
        tax_year=2026,
        regular_periods_closed=11,
        tax_withholding_periods_closed=12,
        trattamento_recognized=Decimal(160),
        trattamento_recovered=Decimal(40),
        recoveries=(RecoveryObligation(tax_year=2026, plan=_PLAN),),
    ).to_state()
    december = regular_period(month=12, opening_state=opening)
    thirteenth = ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.thirteenth(2026, 12),
            payment_date=date(2026, 12, 27),
            employment=Employment(ccnl_slug=COMMERCIO, level_code="4"),
            employer=EMPLOYER,
            opening_state=december.closing_state,
        )
    )
    return december, thirteenth


def _january_2027(opening: PayrollState) -> PeriodResult:
    """Compute January 2027 on 2026 rules standing in for 2027.

    Returns:
        The January 2027 result.
    """
    return _NEXT_YEAR_ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2027, 1),
            payment_date=date(2027, 1, 27),
            employment=Employment(ccnl_slug=COMMERCIO, level_code="4"),
            employer=EMPLOYER,
            opening_state=opening,
        )
    )


def test_installment_recovery_survives_the_year_change() -> None:
    """D.L. 3/2020 art. 1 c. 3: recovery above 60 EUR runs in 8 installments.

    A plan of 160.00 EUR in 8 installments of 20.00 with 2 posted before
    December posts the third in December and the fourth on the tredicesima,
    leaving 4 installments (80.00) for 2027.  The state that opens 2027 has
    fresh year-to-date accounts and still carries them.
    """
    _, thirteenth = _december_2026()

    next_year = ENGINE.close_tax_year(thirteenth.closing_state)

    (carried,) = next_year.obligations.recoveries
    assert carried.tax_year == 2026
    assert carried.plan.installments_posted == 4
    assert carried.plan.residual == Decimal("80.00")
    assert next_year.ytd == TaxYearState(tax_year=2027)


def test_close_tax_year_rejects_a_state_before_the_last_run() -> None:
    """The tredicesima is still due: 2026 cannot be closed after December."""
    december, _ = _december_2026()

    with pytest.raises(InvalidInputError, match="13 of 14 withholding slots"):
        ENGINE.close_tax_year(december.closing_state)


def test_carried_installment_is_deducted_in_the_next_year() -> None:
    """January 2027 deducts the fifth installment and keeps its own credit.

    Differential oracle on the same 2027 run with and without the carried
    plan: net pay is exactly 20.00 lower, the plan moves from 4 to 5 posted
    (residual 60.00), and the 2027 trattamento integrativo account is the
    same as without the plan, because a 2026 recovery is not a 2027 credit.
    """
    _, thirteenth = _december_2026()
    opening = ENGINE.close_tax_year(thirteenth.closing_state)

    with_plan = _january_2027(opening)
    without_plan = _january_2027(PayrollState(ytd=opening.ytd))

    assert without_plan.period_net - with_plan.period_net == Decimal("20.00")
    (carried,) = with_plan.closing_state.obligations.recoveries
    assert carried.plan.installments_posted == 5
    assert carried.plan.residual == Decimal("60.00")
    assert with_plan.closing_state.ytd == without_plan.closing_state.ytd
    recovery = [
        item
        for item in with_plan.pay_items
        if item.item_id == "trattamento_integrativo_recovery_2026_2027-01-regular"
    ]
    assert [item.amount for item in recovery] == [Decimal(-20)]
    (decision,) = [
        d
        for d in with_plan.decisions
        if d.capability == "trattamento_integrativo_recovery"
    ]
    assert decision.reason_code == "installment_posted"
    assert decision.amount == Decimal(-20)
    assert decision.inputs["origin_tax_year"] == "2026"
    assert decision.inputs["installment_number"] == Decimal(5)
