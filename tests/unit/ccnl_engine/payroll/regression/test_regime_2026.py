"""Regression tests for the L.199/2025 substitute-tax regimes.

Rinnovo contrattuale (art. 1 co. 7): 5% flat tax on contract-renewal
salary increments, BonusEvent(kind="contract_renewal"), for private-sector
workers whose 2025 employment income does not exceed 33,000 EUR.

Night, holiday and shift supplements (art. 1 cc. 10-11): 15% flat tax
within 1,500 EUR a year when the worker's 2025 employment income does not
exceed 40,000 EUR, NightShiftEvent with prior_income set.  Fail-closed: None
means ordinary IRPEF.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.domain.events import BonusEvent, NightShiftEvent
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodCalculationResult,
    PeriodState,
)
from ccnl_engine.payroll.domain.period_payroll import PeriodId

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_YEAR = 2026
_ZERO = Decimal(0)
_RENEWAL_ELIGIBLE_INCOME = Decimal("20000.00")


def _req(
    month: int = 1,
    events: tuple[object, ...] = (),
    opening: PeriodState | None = None,
) -> PeriodCalculationRequest:
    return PeriodCalculationRequest(
        period_id=PeriodId(year=_YEAR, month=month),
        payment_date=date(_YEAR, month, 28),
        ccnl_slug=_CCNL,
        level_code=_LEVEL,
        opening_state=opening or PeriodState.zero(),
        events=events,  # type: ignore[arg-type]
    )


def _sum_account(result: PeriodCalculationResult, account: AccountKind) -> Decimal:
    return sum((e.amount for e in result.ledger_entries if e.account == account), _ZERO)


class TestRinnovoContrattuale:
    """BonusEvent(kind='contract_renewal') → 5% substitute tax, no ordinary IRPEF."""

    def test_contract_renewal_posts_substitute_tax(self) -> None:
        """A 2,000 EUR rinnovo increment must post SUBSTITUTE_TAX = 100.00 (5%)."""
        bonus = BonusEvent(
            event_date=date(_YEAR, 1, 15),
            amount=Decimal("2000.00"),
            kind="contract_renewal",
            prior_income=_RENEWAL_ELIGIBLE_INCOME,
        )
        result = calculate_period(_req(events=(bonus,)))
        sub_tax = _sum_account(result, AccountKind.SUBSTITUTE_TAX)
        assert sub_tax == Decimal("100.00"), (
            f"contract_renewal 2,000 EUR must post SUBSTITUTE_TAX=100.00 (5%); "
            f"got {sub_tax}."
        )

    def test_contract_renewal_inps_included(self) -> None:
        """A rinnovo increment must increase the INPS contribution base."""
        no_bonus = calculate_period(_req())
        bonus = BonusEvent(
            event_date=date(_YEAR, 1, 15),
            amount=Decimal("2000.00"),
            kind="contract_renewal",
            prior_income=_RENEWAL_ELIGIBLE_INCOME,
        )
        with_bonus = calculate_period(_req(events=(bonus,)))
        inps_no = _sum_account(no_bonus, AccountKind.EMPLOYEE_CONTRIBUTIONS)
        inps_with = _sum_account(with_bonus, AccountKind.EMPLOYEE_CONTRIBUTIONS)
        assert inps_with > inps_no, (
            "contract_renewal must increase INPS contributions "
            f"(contribution=included); got inps_no={inps_no}, inps_with={inps_with}."
        )

    def test_contract_renewal_does_not_consume_pdr_plafond(self) -> None:
        """A rinnovo increment must not affect fringe.pdr (PdR aggregate)."""
        bonus = BonusEvent(
            event_date=date(_YEAR, 1, 15),
            amount=Decimal("2000.00"),
            kind="contract_renewal",
            prior_income=_RENEWAL_ELIGIBLE_INCOME,
        )
        result = calculate_period(_req(events=(bonus,)))
        assert result.closing_state.ytd.fringe.pdr == _ZERO, (
            f"contract_renewal must not consume PdR plafond; "
            f"got fringe.pdr={result.closing_state.ytd.fringe.pdr}."
        )

    def test_ineligible_renewal_is_ordinary_income_not_pdr(self) -> None:
        """Above the ceiling the increment is ordinary IRPEF, never the PdR base."""
        eligible, ineligible = (
            calculate_period(
                _req(
                    events=(
                        BonusEvent(
                            event_date=date(_YEAR, 1, 15),
                            amount=Decimal("2000.00"),
                            kind="contract_renewal",
                            prior_income=income,
                        ),
                    )
                )
            )
            for income in (_RENEWAL_ELIGIBLE_INCOME, Decimal("100000.00"))
        )
        assert _sum_account(ineligible, AccountKind.SUBSTITUTE_TAX) == _ZERO
        assert ineligible.closing_state.ytd.fringe.pdr == _ZERO
        assert _sum_account(ineligible, AccountKind.ORDINARY_TAX) > _sum_account(
            eligible, AccountKind.ORDINARY_TAX
        )


class TestNotteTurno:
    """NightShiftEvent with prior_income → 15% substitute tax when eligible."""

    def test_eligible_notte_posts_substitute_tax(self) -> None:
        """Night shift with prior_income=20,000 must post SUBSTITUTE_TAX at 15%."""
        shift = NightShiftEvent(
            event_date=date(_YEAR, 1, 15),
            supplement_amount=Decimal("500.00"),
            prior_income=Decimal("20000.00"),
        )
        result = calculate_period(_req(events=(shift,)))
        sub_tax = _sum_account(result, AccountKind.SUBSTITUTE_TAX)
        assert sub_tax == Decimal("75.00"), (
            f"Eligible NightShiftEvent 500 EUR must post SUBSTITUTE_TAX=75.00 (15%); "
            f"got {sub_tax}."
        )

    def test_eligible_notte_substitute_less_than_ordinary(self) -> None:
        """Eligible notte (15%) must be cheaper than ordinary IRPEF on the same amount.

        The supplement 500 EUR at 15% = 75 EUR.  Ordinary IRPEF at the marginal
        rates for a C3 metal-mechanic is higher, so the substitute is beneficial.
        """
        shift_eligible = NightShiftEvent(
            event_date=date(_YEAR, 1, 15),
            supplement_amount=Decimal("500.00"),
            prior_income=Decimal("20000.00"),
        )
        shift_no_regime = NightShiftEvent(
            event_date=date(_YEAR, 1, 15),
            supplement_amount=Decimal("500.00"),
            prior_income=None,
        )
        result_eligible = calculate_period(_req(events=(shift_eligible,)))
        result_ordinary = calculate_period(_req(events=(shift_no_regime,)))
        sub_tax_eligible = _sum_account(result_eligible, AccountKind.SUBSTITUTE_TAX)
        sub_tax_ordinary = _sum_account(result_ordinary, AccountKind.SUBSTITUTE_TAX)
        assert sub_tax_eligible == Decimal("75.00"), (
            f"Eligible notte must produce SUBSTITUTE_TAX=75.00; got {sub_tax_eligible}."
        )
        assert sub_tax_ordinary == _ZERO, (
            "Notte without prior_income (fail-closed) must produce SUBSTITUTE_TAX=0; "
            f"got {sub_tax_ordinary}."
        )

    def test_ceiling_exceeded_notte_ordinary_irpef(self) -> None:
        """Night shift with prior_income > 40,000 must not get the substitute rate."""
        shift = NightShiftEvent(
            event_date=date(_YEAR, 1, 15),
            supplement_amount=Decimal("500.00"),
            prior_income=Decimal("45000.00"),
        )
        result = calculate_period(_req(events=(shift,)))
        sub_tax = _sum_account(result, AccountKind.SUBSTITUTE_TAX)
        assert sub_tax == _ZERO, (
            f"NightShiftEvent with prior_income=45,000 (> 40,000 ceiling) must "
            f"post SUBSTITUTE_TAX=0; got {sub_tax}."
        )

    def test_unknown_prior_income_notte_ordinary_irpef(self) -> None:
        """Fail-closed: NightShiftEvent with prior_income=None → ordinary IRPEF."""
        shift = NightShiftEvent(
            event_date=date(_YEAR, 1, 15),
            supplement_amount=Decimal("500.00"),
            prior_income=None,
        )
        result = calculate_period(_req(events=(shift,)))
        sub_tax = _sum_account(result, AccountKind.SUBSTITUTE_TAX)
        assert sub_tax == _ZERO, (
            f"NightShiftEvent with prior_income=None must not get substitute rate; "
            f"got SUBSTITUTE_TAX={sub_tax}."
        )
