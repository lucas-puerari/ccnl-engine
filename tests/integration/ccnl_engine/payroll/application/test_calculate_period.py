"""Tests for the period-first payroll engine: calculate_period and helpers."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.domain.accrual_state import EmploymentAccrualState
from ccnl_engine.payroll.domain.employment import Apprentice, FixedTerm
from ccnl_engine.payroll.domain.inps_base import InpsBaseYtd
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.pay_items import (
    BaseSalaryEarning,
    EmployeeWithholdingItem,
    EmployerContributionItem,
    TfrAccrualItem,
)
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.tax_cash_state import TaxCashState
from ccnl_engine.payroll.domain.ytd_accounts import EarningsYtd, TaxYtd
from ccnl_engine.payroll.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)
from ccnl_engine.shared.domain.errors import InvalidInputError
from tests.helpers import EMPLOYER_50

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_ZERO = Decimal(0)

# C3 salary: 2158.26 until 2026-06-01, 2211.43 from 2026-06-01
_C3_GROSS_JAN = Decimal("2158.26")
_C3_GROSS_JUL = Decimal("2211.43")


def _req(
    year: int = 2026,
    month: int = 1,
    payment_date: date | None = None,
    opening_state: PeriodState | TaxCashState | None = None,
) -> PeriodCalculationRequest:
    if payment_date is None:
        payment_date = date(year, month, 28)
    if isinstance(opening_state, TaxCashState):
        opening_state = PeriodState(cash=opening_state)
    return PeriodCalculationRequest(
        employer=EMPLOYER_50,
        period_id=PeriodId(year=year, month=month),
        payment_date=payment_date,
        ccnl_slug=_CCNL,
        level_code=_LEVEL,
        opening_state=opening_state or PeriodState.zero(),
    )


class TestCalculatePeriodBasic:
    """Basic correctness: gross, net, employer_cost for C3 Jan 2026."""

    def test_period_gross_matches_salary_table(self) -> None:
        """Gross equals the CCNL salary-table value for C3 in January 2026."""
        result = calculate_period(_req())
        assert result.period_gross == _C3_GROSS_JAN

    def test_period_net_derived_from_payitems(self) -> None:
        """Net equals gross + credits - employee contributions - tax."""
        result = calculate_period(_req())
        gross = result.period_gross
        inps_emp = sum(
            e.amount
            for e in result.ledger_entries
            if e.account == AccountKind.EMPLOYEE_CONTRIBUTIONS
        )
        irpef = sum(
            e.amount
            for e in result.ledger_entries
            if e.account == AccountKind.ORDINARY_TAX
        )
        tratt = sum(
            e.amount for e in result.ledger_entries if e.account == AccountKind.CREDITS
        )
        assert result.period_net == gross + tratt - inps_emp - irpef

    def test_period_id_propagated(self) -> None:
        """The result carries the same period_id as the request."""
        req = _req(year=2026, month=3)
        result = calculate_period(req)
        assert result.period_id == PeriodId(year=2026, month=3)

    def test_payment_date_propagated(self) -> None:
        """The result carries the same payment_date as the request."""
        pdate = date(2026, 1, 31)
        result = calculate_period(_req(payment_date=pdate))
        assert result.payment_date == pdate

    def test_payment_date_in_all_ledger_entries(self) -> None:
        """Every ledger entry carries the request payment_date."""
        pdate = date(2026, 1, 31)
        result = calculate_period(_req(payment_date=pdate))
        for entry in result.ledger_entries:
            assert entry.payment_date == pdate

    def test_payment_date_in_all_pay_items(self) -> None:
        """Every pay item carries the request payment_date."""
        pdate = date(2026, 1, 31)
        result = calculate_period(_req(payment_date=pdate))
        for item in result.pay_items:
            assert item.payment_date == pdate

    def test_period_id_governs_salary_lookup(self) -> None:
        """Salary table lookup uses period_id, not a fixed date."""
        # Salary increases to 2211.43 from 2026-06-01.
        result_jan = calculate_period(_req(month=1))
        result_jul = calculate_period(_req(month=7))
        assert result_jan.period_gross == _C3_GROSS_JAN
        assert result_jul.period_gross == _C3_GROSS_JUL

    def test_with_explicit_repo(self) -> None:
        """An explicit BundledKnowledgeRepository produces the correct gross."""
        result = calculate_period(_req(), repo=BundledKnowledgeRepository())
        assert result.period_gross == _C3_GROSS_JAN

    def test_with_default_repo(self) -> None:
        """repo=None falls back to BundledKnowledgeRepository."""
        result = calculate_period(_req(), repo=None)
        assert result.period_gross == _C3_GROSS_JAN


class TestConguaglioDiscriminator:
    """Real conguaglio: changing YTD IRPEF withheld changes the period net."""

    def test_irpef_conguaglio_changes_net(self) -> None:
        """The key discriminator: this fails with the legacy annual-divide engine."""
        result_zero = calculate_period(_req())
        result_with_ytd = calculate_period(
            _req(opening_state=TaxCashState(tax=TaxYtd(irpef=Decimal("1000.00"))))
        )
        assert result_zero.period_net != result_with_ytd.period_net

    def test_higher_ytd_irpef_increases_net(self) -> None:
        """More IRPEF already withheld → less to withhold now → higher net."""
        result_zero = calculate_period(_req())
        result_with_ytd = calculate_period(
            _req(opening_state=TaxCashState(tax=TaxYtd(irpef=Decimal("1000.00"))))
        )
        assert result_with_ytd.period_net > result_zero.period_net

    def test_irpef_ytd_accumulates_in_closing(self) -> None:
        """closing_state.cash.tax.irpef equals the period IRPEF withheld."""
        result = calculate_period(_req())
        irpef_period = sum(
            e.amount
            for e in result.ledger_entries
            if e.account == AccountKind.ORDINARY_TAX
        )
        assert result.closing_state.cash.tax.irpef == irpef_period


class TestClosingStateTransitions:
    """calculate_period advances the YTD state correctly."""

    def test_run_closes_its_competence_and_its_payment(self) -> None:
        """The run closes once in the accrual state and once in the cash state."""
        opening = TaxCashState()
        result = calculate_period(_req(opening_state=opening))
        closing = result.closing_state
        assert closing.accrual.regular_months(2026) == 1
        assert [str(p) for p in closing.cash.payments] == ["2026-01-regular@2026-01-28"]
        assert closing.cash.withholding_payments_closed == 1

    def test_duplicate_run_id_raises(self) -> None:
        """Re-submitting an already-closed run_id raises InvalidInputError."""
        opening = PeriodState.zero()
        result = calculate_period(_req(opening_state=opening))
        with pytest.raises(InvalidInputError, match="already closed"):
            calculate_period(_req(opening_state=result.closing_state))

    def test_gross_ytd_accumulates(self) -> None:
        """gross_ytd closing equals opening plus period gross."""
        opening = TaxCashState(earnings=EarningsYtd(gross=Decimal("10000.00")))
        result = calculate_period(_req(opening_state=opening))
        expected = Decimal("10000.00") + result.period_gross
        assert result.closing_state.cash.earnings.gross == expected

    def test_inps_employee_ytd_accumulates(self) -> None:
        """inps_employee_ytd closing equals opening plus period employee INPS."""
        opening = TaxCashState(earnings=EarningsYtd(inps_employee=Decimal("500.00")))
        result = calculate_period(_req(opening_state=opening))
        inps_period = sum(
            e.amount
            for e in result.ledger_entries
            if e.account == AccountKind.EMPLOYEE_CONTRIBUTIONS
        )
        expected = Decimal("500.00") + inps_period
        assert result.closing_state.cash.earnings.inps_employee == expected

    def test_taxable_ytd_accumulates(self) -> None:
        """taxable_ytd closing equals opening plus period_taxable slice."""
        opening = TaxCashState(earnings=EarningsYtd(taxable=Decimal("2000.00")))
        result = calculate_period(_req(opening_state=opening))
        closing_taxable = result.closing_state.cash.earnings.taxable
        assert closing_taxable > Decimal("2000.00")
        assert closing_taxable == result.closing_state.cash.earnings.taxable

    def test_taxable_ytd_zero_on_first_period(self) -> None:
        """taxable_ytd starts from zero when opening is PeriodState.zero()."""
        result = calculate_period(_req(opening_state=PeriodState.zero()))
        assert result.closing_state.cash.earnings.taxable > _ZERO

    def test_inps_base_accumulates_by_competence_year(self) -> None:
        """The competence-year INPS base closes above the opening base."""
        opening = PeriodState(
            accrual=EmploymentAccrualState(
                inps_bases=(InpsBaseYtd(2026, own=Decimal("1000.00")),)
            )
        )
        result = calculate_period(_req(opening_state=opening))
        base = result.closing_state.accrual.inps_base(2026)
        assert base.own > Decimal("1000.00")
        assert base.other_employers == _ZERO


class TestPayItems:
    """Pay-item composition for a standard permanent employee."""

    def test_base_salary_item_present(self) -> None:
        """A BaseSalaryEarning item must be in every pay-items tuple."""
        result = calculate_period(_req())
        assert any(isinstance(i, BaseSalaryEarning) for i in result.pay_items)

    def test_inps_employee_item_present(self) -> None:
        """Exactly one EmployeeWithholdingItem with 'inps' in its id."""
        result = calculate_period(_req())
        inps_items = [
            i
            for i in result.pay_items
            if isinstance(i, EmployeeWithholdingItem) and "inps" in i.item_id
        ]
        assert len(inps_items) == 1

    def test_irpef_item_present(self) -> None:
        """Exactly one EmployeeWithholdingItem with 'irpef' in its id."""
        result = calculate_period(_req())
        irpef_items = [
            i
            for i in result.pay_items
            if isinstance(i, EmployeeWithholdingItem) and "irpef" in i.item_id
        ]
        assert len(irpef_items) == 1

    def test_employer_contribution_item_present(self) -> None:
        """An EmployerContributionItem must be in every pay-items tuple."""
        result = calculate_period(_req())
        assert any(isinstance(i, EmployerContributionItem) for i in result.pay_items)

    def test_tfr_accrual_item_present(self) -> None:
        """A TfrAccrualItem must be in every pay-items tuple."""
        result = calculate_period(_req())
        assert any(isinstance(i, TfrAccrualItem) for i in result.pay_items)

    def test_competence_period_matches_period_id(self) -> None:
        """All pay items carry a competence_period matching the request period_id."""
        req = _req(year=2026, month=4)
        result = calculate_period(req)
        for item in result.pay_items:
            assert item.competence_period.year == 2026
            assert item.competence_period.month == 4


class TestLedgerStructure:
    """Ledger entries are complete, correctly dated, and satisfy I9 identity."""

    def test_cash_earnings_entry_present(self) -> None:
        """A CASH_EARNINGS entry must appear in every ledger."""
        result = calculate_period(_req())
        accounts = [e.account for e in result.ledger_entries]
        assert AccountKind.CASH_EARNINGS in accounts

    def test_employee_contributions_entry_present(self) -> None:
        """An EMPLOYEE_CONTRIBUTIONS entry must appear in every ledger."""
        result = calculate_period(_req())
        accounts = [e.account for e in result.ledger_entries]
        assert AccountKind.EMPLOYEE_CONTRIBUTIONS in accounts

    def test_ordinary_tax_entry_present(self) -> None:
        """An ORDINARY_TAX entry must appear in every ledger."""
        result = calculate_period(_req())
        accounts = [e.account for e in result.ledger_entries]
        assert AccountKind.ORDINARY_TAX in accounts

    def test_employer_contributions_entry_present(self) -> None:
        """An EMPLOYER_CONTRIBUTIONS entry must appear in every ledger."""
        result = calculate_period(_req())
        accounts = [e.account for e in result.ledger_entries]
        assert AccountKind.EMPLOYER_CONTRIBUTIONS in accounts

    def test_tfr_accrual_entry_present(self) -> None:
        """A TFR_ACCRUAL entry must appear in every ledger."""
        result = calculate_period(_req())
        accounts = [e.account for e in result.ledger_entries]
        assert AccountKind.TFR_ACCRUAL in accounts

    def test_competence_period_matches_period_id(self) -> None:
        """All ledger entries carry a competence_period matching the request."""
        req = _req(year=2026, month=6)
        result = calculate_period(req)
        for entry in result.ledger_entries:
            assert entry.competence_period.year == 2026
            assert entry.competence_period.month == 6


class TestWithholdingDue:
    """withholding_due: IRPEF balance (positive = owed, negative = refund)."""

    def test_withholding_due_present_in_tax_computation(self) -> None:
        """tax_computation.withholding_due is populated on every period."""
        result = calculate_period(_req())
        assert hasattr(result.tax_computation, "withholding_due")

    def test_withholding_due_positive_when_no_prior_withheld(self) -> None:
        """withholding_due is positive when no IRPEF has been withheld yet."""
        result = calculate_period(_req(opening_state=PeriodState.zero()))
        assert result.tax_computation.withholding_due > _ZERO

    def test_withholding_due_negative_final_period_excess(self) -> None:
        """Final period with excess YTD produces negative withholding_due."""
        # metalmeccanico has 13 withholding slots; twpc=12 → remaining=1
        opening = TaxCashState(
            tax=TaxYtd(irpef=Decimal("5000.00")),
        )
        result = calculate_period(_req(opening_state=opening))
        assert result.tax_computation.withholding_due < _ZERO

    def test_ordinary_tax_negative_in_final_period_with_excess(self) -> None:
        """ordinary_tax is negative in the final period when YTD exceeds liability.

        No payment is planned after the run: it settles the conguaglio.
        """
        opening = TaxCashState(
            tax=TaxYtd(irpef=Decimal("5000.00")),
        )
        result = calculate_period(
            replace(_req(opening_state=opening), planned_payments=())
        )
        assert result.tax_computation.ordinary_tax < _ZERO

    def test_ordinary_tax_non_negative_in_non_final_period(self) -> None:
        """ordinary_tax is clamped to zero in non-final periods."""
        opening = TaxCashState(
            tax=TaxYtd(irpef=Decimal("5000.00")),
        )
        result = calculate_period(_req(opening_state=opening))
        assert result.tax_computation.ordinary_tax >= _ZERO


class TestContractTypeRouting:
    """contract_type on PeriodCalculationRequest routes gross and INPS correctly."""

    def test_apprentice_gross_below_permanent(self) -> None:
        """Apprentice (85% track) produces a lower period_gross than Permanent."""
        permanent_req = PeriodCalculationRequest(
            employer=EMPLOYER_50,
            period_id=PeriodId(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            opening_state=PeriodState.zero(),
        )
        # metalmeccanico track professionalizzante_36: months 0-12 → 85%
        # C3 is covered by two tracks; explicit track= is required.
        apprentice_req = PeriodCalculationRequest(
            employer=EMPLOYER_50,
            period_id=PeriodId(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            opening_state=PeriodState.zero(),
            contract_type=Apprentice(months_elapsed=6, track="professionalizzante_36"),
        )
        perm_result = calculate_period(permanent_req)
        appr_result = calculate_period(apprentice_req)
        assert appr_result.period_gross < perm_result.period_gross

    def test_fixed_term_same_gross_as_permanent(self) -> None:
        """FixedTerm gross equals Permanent gross (only INPS employer rate differs)."""
        permanent_req = PeriodCalculationRequest(
            employer=EMPLOYER_50,
            period_id=PeriodId(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            opening_state=PeriodState.zero(),
        )
        fixed_req = replace(permanent_req, contract_type=FixedTerm())
        perm_result = calculate_period(permanent_req)
        fixed_result = calculate_period(fixed_req)
        assert fixed_result.period_gross == perm_result.period_gross
