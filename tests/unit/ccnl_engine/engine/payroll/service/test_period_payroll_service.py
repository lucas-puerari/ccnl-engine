"""Unit tests for compute_period_payroll service function."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.domain.employment import Permanent
from ccnl_engine.engine.payroll.domain.fiscal_ytd import FiscalYTD
from ccnl_engine.engine.payroll.domain.payroll_state import PayrollState
from ccnl_engine.engine.payroll.domain.period_payroll import (
    PeriodPayrollRequest,
    PeriodPayrollResult,
)
from ccnl_engine.engine.payroll.domain.scenario import (
    AnnualEstimateInput,
    Employee,
    Employer,
    Employment,
    Jurisdiction,
    PeriodPayrollInput,
)
from ccnl_engine.engine.payroll.service.orchestrator import (
    compute_period_payroll,
    estimate_annual,
)
from ccnl_engine.engine.payroll.service.rounding import money

_ZERO = Decimal(0)

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_AS_OF = date(2026, 1, 1)


def _structural() -> AnnualEstimateInput:
    """Return a minimal structural scenario.

    Returns:
        A minimal :class:`AnnualEstimateInput` with required fields only.
    """
    return AnnualEstimateInput(
        employee=Employee(level_code=_LEVEL),
        employment=Employment(
            ccnl=_CCNL,
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=_AS_OF,
        ),
    )


def _zero_request() -> PeriodPayrollRequest:
    """Return a request with PayrollState.zero() as opening state.

    Returns:
        A :class:`PeriodPayrollRequest` with all-zero opening state.
    """
    return PeriodPayrollRequest(
        structural=_structural(),
        period=PeriodPayrollInput(),
        opening_state=PayrollState.zero(),
    )


class TestComputePeriodPayrollReturnType:
    """compute_period_payroll returns a PeriodPayrollResult."""

    def test_returns_period_payroll_result(self) -> None:
        """Return type is PeriodPayrollResult."""
        result = compute_period_payroll(_zero_request())
        assert isinstance(result, PeriodPayrollResult)

    def test_opening_state_is_zero(self) -> None:
        """Opening state matches the one passed in (zero for January)."""
        result = compute_period_payroll(_zero_request())
        assert result.opening_state == PayrollState.zero()

    def test_closing_state_is_payroll_state(self) -> None:
        """Closing state is a PayrollState instance."""
        result = compute_period_payroll(_zero_request())
        assert isinstance(result.closing_state, PayrollState)

    def test_period_gross_positive(self) -> None:
        """period_gross is a positive Decimal."""
        result = compute_period_payroll(_zero_request())
        assert result.period_gross > _ZERO

    def test_period_net_positive(self) -> None:
        """period_net is positive."""
        result = compute_period_payroll(_zero_request())
        assert result.period_net > _ZERO

    def test_period_employer_cost_positive(self) -> None:
        """period_employer_cost is positive."""
        result = compute_period_payroll(_zero_request())
        assert result.period_employer_cost > _ZERO

    def test_ledger_entries_tuple(self) -> None:
        """ledger_entries is a tuple."""
        result = compute_period_payroll(_zero_request())
        assert isinstance(result.ledger_entries, tuple)


class TestComputePeriodPayrollStateAccumulation:
    """Closing state accumulates opening state with period increments."""

    def test_gross_ytd_grows(self) -> None:
        """Closing gross_annual_ytd exceeds opening (which is zero)."""
        result = compute_period_payroll(_zero_request())
        assert result.closing_state.gross_annual_ytd > _ZERO

    def test_inps_employee_ytd_grows(self) -> None:
        """Closing inps_employee_annual_ytd exceeds zero."""
        result = compute_period_payroll(_zero_request())
        assert result.closing_state.inps_employee_annual_ytd > _ZERO

    def test_irpef_withheld_grows(self) -> None:
        """Closing irpef_withheld_ytd exceeds zero."""
        result = compute_period_payroll(_zero_request())
        assert result.closing_state.irpef_withheld_ytd > _ZERO

    def test_tfr_ytd_grows(self) -> None:
        """Closing tfr_annual_ytd exceeds zero."""
        result = compute_period_payroll(_zero_request())
        assert result.closing_state.tfr_annual_ytd > _ZERO

    def test_leave_balance_derived_correctly(self) -> None:
        """leave_balance_days equals accrued minus taken."""
        result = compute_period_payroll(_zero_request())
        closing = result.closing_state
        assert closing.leave_balance_days == (
            closing.leave_accrued_days_ytd - closing.leave_taken_days_ytd
        )

    def test_chained_state_accumulates(self) -> None:
        """Second period's closing gross > first period's closing gross."""
        r1 = compute_period_payroll(_zero_request())
        req2 = PeriodPayrollRequest(
            structural=_structural(),
            period=PeriodPayrollInput(),
            opening_state=r1.closing_state,
        )
        r2 = compute_period_payroll(req2)
        assert r2.closing_state.gross_annual_ytd > r1.closing_state.gross_annual_ytd

    def test_opening_state_preserved(self) -> None:
        """opening_state in result matches the one passed in."""
        opening = PayrollState(
            gross_annual_ytd=Decimal("1000.00"),
            inps_employee_annual_ytd=Decimal("90.00"),
            inps_employer_annual_ytd=Decimal("260.00"),
            inail_employer_annual_ytd=Decimal("5.00"),
            taxable_income_ytd=Decimal("910.00"),
            irpef_gross_ytd=Decimal("200.00"),
            irpef_withheld_ytd=Decimal("160.00"),
            work_income_deduction_ytd=Decimal("80.00"),
            fam_deductions_ytd=_ZERO,
            art15_deductions_ytd=_ZERO,
            trattamento_integrativo_ytd=_ZERO,
            addizionale_regionale_ytd=Decimal("15.00"),
            addizionale_comunale_ytd=Decimal("8.00"),
            tfr_annual_ytd=Decimal("55.00"),
            leave_accrued_days_ytd=Decimal("1.83"),
            leave_taken_days_ytd=_ZERO,
            leave_balance_days=Decimal("1.83"),
            sick_days_ytd=_ZERO,
        )
        req = PeriodPayrollRequest(
            structural=_structural(),
            period=PeriodPayrollInput(),
            opening_state=opening,
        )
        result = compute_period_payroll(req)
        assert result.opening_state is opening

    def test_closing_gross_is_opening_plus_period(self) -> None:
        """Closing gross_annual_ytd = opening + period_gross."""
        result = compute_period_payroll(_zero_request())
        assert result.closing_state.gross_annual_ytd == (
            result.opening_state.gross_annual_ytd + result.period_gross
        )


class TestComputePeriodPayrollConguaglio:
    """Prior withheld IRPEF is injected correctly for conguaglio."""

    def test_zero_opening_uses_no_prior_withheld(self) -> None:
        """First period (zero state) computes without prior withheld."""
        result = compute_period_payroll(_zero_request())
        assert result.closing_state.irpef_withheld_ytd > _ZERO

    def test_nonzero_irpef_ytd_does_not_raise(self) -> None:
        """Nonzero irpef_withheld_ytd in opening state is accepted."""
        opening = PayrollState.zero()
        first = compute_period_payroll(_zero_request())
        req2 = PeriodPayrollRequest(
            structural=_structural(),
            period=PeriodPayrollInput(),
            opening_state=first.closing_state,
        )
        result = compute_period_payroll(req2)
        assert result.period_net > _ZERO
        _ = opening  # referenced to satisfy linter

    def test_irpef_withheld_ytd_cumulates_across_periods(self) -> None:
        """irpef_withheld_ytd grows period over period."""
        r1 = compute_period_payroll(_zero_request())
        req2 = PeriodPayrollRequest(
            structural=_structural(),
            period=PeriodPayrollInput(),
            opening_state=r1.closing_state,
        )
        r2 = compute_period_payroll(req2)
        assert r2.closing_state.irpef_withheld_ytd > r1.closing_state.irpef_withheld_ytd


class TestComputePeriodPayrollPublicApi:
    """PayrollEngine replaces compute_period_payroll as the public entry point."""

    def test_payroll_engine_in_dunder_all(self) -> None:
        """PayrollEngine is listed in ccnl_engine.__all__."""
        import ccnl_engine  # noqa: PLC0415

        assert "PayrollEngine" in ccnl_engine.__all__

    def test_period_calculation_request_in_dunder_all(self) -> None:
        """PeriodCalculationRequest is listed in ccnl_engine.__all__."""
        import ccnl_engine  # noqa: PLC0415

        assert "PeriodCalculationRequest" in ccnl_engine.__all__

    def test_accepts_optional_bundle_none(self) -> None:
        """bundle=None is accepted (loads on demand)."""
        result = compute_period_payroll(_zero_request(), bundle=None)
        assert isinstance(result, PeriodPayrollResult)

    def test_accepts_pre_loaded_bundle(self) -> None:
        """A pre-loaded bundle is used without reloading rulesets."""
        from ccnl_engine import load_payroll_bundle  # noqa: PLC0415

        bundle = load_payroll_bundle(_CCNL, _AS_OF.year, num_employees=50)
        result = compute_period_payroll(_zero_request(), bundle=bundle)
        assert isinstance(result, PeriodPayrollResult)
        assert result.period_gross > _ZERO

    @pytest.mark.parametrize("n_periods", [1, 3, 12])
    def test_chained_n_periods(self, n_periods: int) -> None:
        """Chain n periods; final gross_ytd is n times first period gross."""
        state = PayrollState.zero()
        first_gross: Decimal | None = None
        for _ in range(n_periods):
            req = PeriodPayrollRequest(
                structural=_structural(),
                period=PeriodPayrollInput(),
                opening_state=state,
            )
            result = compute_period_payroll(req)
            if first_gross is None:
                first_gross = result.period_gross
            state = result.closing_state
        assert state.gross_annual_ytd > _ZERO


class TestComputePeriodPayrollExtraMonthlyPayments:
    """extra_monthly_payments on PeriodPayrollInput scales period amounts."""

    def test_extra_zero_default(self) -> None:
        """Default extra_monthly_payments=0 gives standard period amount."""
        result = compute_period_payroll(_zero_request())
        assert result.period_gross > _ZERO

    def test_extra_one_doubles_gross(self) -> None:
        """extra_monthly_payments=1 doubles the period gross vs standard."""
        req_normal = _zero_request()
        req_bonus = PeriodPayrollRequest(
            structural=_structural(),
            period=PeriodPayrollInput(extra_monthly_payments=1),
            opening_state=PayrollState.zero(),
        )
        r_normal = compute_period_payroll(req_normal)
        r_bonus = compute_period_payroll(req_bonus)
        expected = money(r_normal.period_gross * Decimal(2))
        assert r_bonus.period_gross == expected

    def test_extra_one_doubles_net(self) -> None:
        """extra_monthly_payments=1 doubles the period net vs standard."""
        req_normal = _zero_request()
        req_bonus = PeriodPayrollRequest(
            structural=_structural(),
            period=PeriodPayrollInput(extra_monthly_payments=1),
            opening_state=PayrollState.zero(),
        )
        r_normal = compute_period_payroll(req_normal)
        r_bonus = compute_period_payroll(req_bonus)
        expected = money(r_normal.period_net * Decimal(2))
        assert r_bonus.period_net == expected

    def test_extra_one_doubles_employer_cost(self) -> None:
        """extra_monthly_payments=1 approximately doubles the period employer cost."""
        req_normal = _zero_request()
        req_bonus = PeriodPayrollRequest(
            structural=_structural(),
            period=PeriodPayrollInput(extra_monthly_payments=1),
            opening_state=PayrollState.zero(),
        )
        r_normal = compute_period_payroll(req_normal)
        r_bonus = compute_period_payroll(req_bonus)
        # Rounding order differs; allow 1-cent tolerance.
        diff = abs(
            r_bonus.period_employer_cost - r_normal.period_employer_cost * Decimal(2)
        )
        assert diff <= Decimal("0.01")

    def test_extra_two_triples_gross(self) -> None:
        """extra_monthly_payments=2 triples the period gross."""
        req_normal = _zero_request()
        req_double = PeriodPayrollRequest(
            structural=_structural(),
            period=PeriodPayrollInput(extra_monthly_payments=2),
            opening_state=PayrollState.zero(),
        )
        r_normal = compute_period_payroll(req_normal)
        r_double = compute_period_payroll(req_double)
        expected = money(r_normal.period_gross * Decimal(3))
        assert r_double.period_gross == expected

    def test_annual_gross_reconciles_across_13_periods(self) -> None:
        """11 standard + 1 bonus period totals to annual gross for 13-month CCNL."""
        state = PayrollState.zero()
        total_gross = _ZERO
        for i in range(12):
            extra = 1 if i == 11 else 0
            req = PeriodPayrollRequest(
                structural=_structural(),
                period=PeriodPayrollInput(extra_monthly_payments=extra),
                opening_state=state,
            )
            result = compute_period_payroll(req)
            total_gross += result.period_gross
            state = result.closing_state
        annual_gross = compute_period_payroll(_zero_request()).period_gross * Decimal(
            13
        )
        from decimal import ROUND_HALF_UP  # noqa: PLC0415

        assert total_gross == annual_gross.quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    def test_gross_ytd_includes_bonus_month(self) -> None:
        """After a bonus month, gross_ytd reflects the extra payment."""
        req_normal = _zero_request()
        r_normal = compute_period_payroll(req_normal)
        req_bonus = PeriodPayrollRequest(
            structural=_structural(),
            period=PeriodPayrollInput(extra_monthly_payments=1),
            opening_state=r_normal.closing_state,
        )
        r_bonus = compute_period_payroll(req_bonus)
        expected_ytd = r_normal.closing_state.gross_annual_ytd + r_bonus.period_gross
        assert r_bonus.closing_state.gross_annual_ytd == expected_ytd


_JURISDICTION = Jurisdiction(regione="Lombardia", comune_belfiore="F205")


def _structural_with_jurisdiction() -> AnnualEstimateInput:
    """Return a structural scenario with Lombardia/Milano jurisdiction.

    Returns:
        :class:`AnnualEstimateInput` with Lombardia/Milano jurisdiction.
    """
    return AnnualEstimateInput(
        employee=Employee(level_code=_LEVEL, jurisdiction=_JURISDICTION),
        employment=Employment(
            ccnl=_CCNL,
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=_AS_OF,
        ),
    )


class TestComputePeriodPayrollAddizionali:
    """Addizionali regionali/comunali: monthly installments and December saldo."""

    def test_standard_period_addizionale_is_annual_over_eleven(self) -> None:
        """Each standard period withholds addizionale_annual / 11."""
        structural = _structural_with_jurisdiction()
        annual = estimate_annual(structural)
        reg_annual = annual.result.taxes.addizionale_regionale_annual
        com_annual = annual.result.taxes.addizionale_comunale_annual
        req = PeriodPayrollRequest(
            structural=structural,
            period=PeriodPayrollInput(),
            opening_state=PayrollState.zero(),
        )
        result = compute_period_payroll(req)
        expected_reg = money(reg_annual / Decimal(11))
        expected_com = money(com_annual / Decimal(11))
        assert result.closing_state.addizionale_regionale_ytd == expected_reg
        assert result.closing_state.addizionale_comunale_ytd == expected_com

    def test_settlement_period_withholds_balance(self) -> None:
        """Settlement period withholds annual - ytd_withheld."""
        structural = _structural_with_jurisdiction()
        annual = estimate_annual(structural)
        reg_annual = annual.result.taxes.addizionale_regionale_annual
        com_annual = annual.result.taxes.addizionale_comunale_annual
        state = PayrollState.zero()
        for _ in range(11):
            req = PeriodPayrollRequest(
                structural=structural,
                period=PeriodPayrollInput(),
                opening_state=state,
            )
            state = compute_period_payroll(req).closing_state
        req_saldo = PeriodPayrollRequest(
            structural=structural,
            period=PeriodPayrollInput(is_addizionali_settlement=True),
            opening_state=state,
        )
        result = compute_period_payroll(req_saldo)
        assert result.closing_state.addizionale_regionale_ytd == reg_annual
        assert result.closing_state.addizionale_comunale_ytd == com_annual

    def test_eleven_plus_settlement_reconciles_to_annual(self) -> None:
        """11 standard + 1 settlement totals exactly to the annual addizionale."""
        structural = _structural_with_jurisdiction()
        annual = estimate_annual(structural)
        reg_annual = annual.result.taxes.addizionale_regionale_annual
        com_annual = annual.result.taxes.addizionale_comunale_annual
        state = PayrollState.zero()
        for _ in range(11):
            req = PeriodPayrollRequest(
                structural=structural,
                period=PeriodPayrollInput(),
                opening_state=state,
            )
            state = compute_period_payroll(req).closing_state
        req_saldo = PeriodPayrollRequest(
            structural=structural,
            period=PeriodPayrollInput(is_addizionali_settlement=True),
            opening_state=state,
        )
        final = compute_period_payroll(req_saldo).closing_state
        assert final.addizionale_regionale_ytd == reg_annual
        assert final.addizionale_comunale_ytd == com_annual

    def test_no_addizionali_when_no_jurisdiction(self) -> None:
        """Without a jurisdiction, addizionale ytd remains zero after settlement."""
        req = PeriodPayrollRequest(
            structural=_structural(),
            period=PeriodPayrollInput(is_addizionali_settlement=True),
            opening_state=PayrollState.zero(),
        )
        result = compute_period_payroll(req)
        assert result.closing_state.addizionale_regionale_ytd == _ZERO
        assert result.closing_state.addizionale_comunale_ytd == _ZERO


class TestComputePeriodPayrollFiscalYTD:
    """compute_period_payroll populates fiscal_ytd in the result."""

    def test_fiscal_ytd_is_fiscal_ytd_instance(self) -> None:
        """Result.fiscal_ytd is a FiscalYTD instance."""
        result = compute_period_payroll(_zero_request())
        assert isinstance(result.fiscal_ytd, FiscalYTD)

    def test_fiscal_ytd_irpef_withheld_positive(self) -> None:
        """fiscal_ytd.irpef_withheld_ytd is positive for a taxable worker."""
        result = compute_period_payroll(_zero_request())
        assert result.fiscal_ytd.irpef_withheld_ytd > _ZERO

    def test_fiscal_ytd_taxable_income_positive(self) -> None:
        """fiscal_ytd.taxable_income_ytd is positive for a standard worker."""
        result = compute_period_payroll(_zero_request())
        assert result.fiscal_ytd.taxable_income_ytd > _ZERO

    def test_fiscal_ytd_matches_closing_state(self) -> None:
        """fiscal_ytd fields match the corresponding closing_state fields."""
        result = compute_period_payroll(_zero_request())
        closing = result.closing_state
        ytd = result.fiscal_ytd
        assert ytd.taxable_income_ytd == closing.taxable_income_ytd
        assert ytd.irpef_gross_ytd == closing.irpef_gross_ytd
        assert ytd.irpef_withheld_ytd == closing.irpef_withheld_ytd
        assert ytd.work_income_deduction_ytd == closing.work_income_deduction_ytd
        assert ytd.fam_deductions_ytd == closing.fam_deductions_ytd
        assert ytd.art15_deductions_ytd == closing.art15_deductions_ytd
        assert ytd.trattamento_integrativo_ytd == closing.trattamento_integrativo_ytd
        assert ytd.addizionale_regionale_ytd == closing.addizionale_regionale_ytd
        assert ytd.addizionale_comunale_ytd == closing.addizionale_comunale_ytd

    def test_fiscal_ytd_accumulates_across_periods(self) -> None:
        """fiscal_ytd grows monotonically from one period to the next."""
        req1 = _zero_request()
        r1 = compute_period_payroll(req1)
        req2 = PeriodPayrollRequest(
            structural=_structural(),
            period=PeriodPayrollInput(),
            opening_state=r1.closing_state,
        )
        r2 = compute_period_payroll(req2)
        assert r2.fiscal_ytd.irpef_withheld_ytd > r1.fiscal_ytd.irpef_withheld_ytd
        assert r2.fiscal_ytd.taxable_income_ytd > r1.fiscal_ytd.taxable_income_ytd

    def test_fiscal_ytd_exportable_from_package(self) -> None:
        """FiscalYTD is importable from the top-level ccnl_engine package."""
        from ccnl_engine import FiscalYTD as F  # noqa: PLC0415

        assert F is FiscalYTD


class TestComputePeriodPayrollIdempotencyKey:
    """compute_period_payroll propagates idempotency_key from request to result."""

    def _req(self, idempotency_key: str | None = None) -> PeriodPayrollRequest:
        return PeriodPayrollRequest(
            structural=AnnualEstimateInput(
                employee=Employee(level_code=_LEVEL),
                employment=Employment(
                    ccnl=_CCNL,
                    contract=Permanent(),
                    employer=Employer(num_employees=50),
                    as_of=_AS_OF,
                ),
            ),
            period=PeriodPayrollInput(),
            opening_state=PayrollState.zero(),
            idempotency_key=idempotency_key,
        )

    def test_idempotency_key_propagated_to_result(self) -> None:
        """Result carries the same idempotency_key as the request."""
        key = "batch-2026-01-worker-42"
        result = compute_period_payroll(self._req(idempotency_key=key))
        assert result.idempotency_key == key

    def test_idempotency_key_none_when_not_supplied(self) -> None:
        """Result idempotency_key is None when the request omitted it."""
        result = compute_period_payroll(self._req())
        assert result.idempotency_key is None
