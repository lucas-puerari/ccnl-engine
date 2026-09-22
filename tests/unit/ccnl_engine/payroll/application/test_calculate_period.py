"""Tests for the period-first payroll engine: calculate_period and helpers."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.engine.errors import InvalidInputError
from ccnl_engine.engine.io.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)
from ccnl_engine.engine.payroll.domain.employment import Apprentice, FixedTerm
from ccnl_engine.engine.payroll.domain.ledger import AccountKind
from ccnl_engine.engine.payroll.domain.pay_items import (
    BaseSalaryEarning,
    EmployeeWithholdingItem,
    EmployerContributionItem,
    TaxCreditItem,
    TfrAccrualItem,
)
from ccnl_engine.engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.engine.tax.domain.credit_rules import TrattamentoIntegrativoRules
from ccnl_engine.payroll.application.calculate_period import (
    _build_pay_items,
    _PeriodAmounts,
    _project_ledger,
    _trattamento_period,
    calculate_period,
)
from ccnl_engine.payroll.domain.events import ArrearsEvent, OvertimeEvent
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodState,
)

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
    opening_state: PeriodState | None = None,
) -> PeriodCalculationRequest:
    if payment_date is None:
        payment_date = date(year, month, 28)
    return PeriodCalculationRequest(
        period_id=PeriodId(year=year, month=month),
        payment_date=payment_date,
        ccnl_slug=_CCNL,
        level_code=_LEVEL,
        opening_state=opening_state or PeriodState.zero(),
    )


def _amounts(*, period_tratt: Decimal = _ZERO) -> _PeriodAmounts:
    return _PeriodAmounts(
        monthly_gross=Decimal("2158.26"),
        inps_employee=Decimal("204.82"),
        inps_employer=Decimal("651.79"),
        tfr=Decimal("159.87"),
        period_irpef=Decimal("279.02"),
        period_tratt=period_tratt,
        period_surtax=_ZERO,
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
            _req(opening_state=PeriodState(irpef_withheld_ytd=Decimal("1000.00")))
        )
        assert result_zero.period_net != result_with_ytd.period_net

    def test_higher_ytd_irpef_increases_net(self) -> None:
        """More IRPEF already withheld → less to withhold now → higher net."""
        result_zero = calculate_period(_req())
        result_with_ytd = calculate_period(
            _req(opening_state=PeriodState(irpef_withheld_ytd=Decimal("1000.00")))
        )
        assert result_with_ytd.period_net > result_zero.period_net

    def test_irpef_ytd_accumulates_in_closing(self) -> None:
        """closing_state.irpef_withheld_ytd equals the period IRPEF withheld."""
        result = calculate_period(_req())
        irpef_period = sum(
            e.amount
            for e in result.ledger_entries
            if e.account == AccountKind.ORDINARY_TAX
        )
        assert result.closing_state.irpef_withheld_ytd == irpef_period


class TestClosingStateTransitions:
    """calculate_period advances the YTD state correctly."""

    def test_months_closed_increments(self) -> None:
        """months_closed increases by exactly 1 per period."""
        opening = PeriodState(months_closed=5)
        result = calculate_period(_req(opening_state=opening))
        assert result.closing_state.months_closed == 6

    def test_gross_ytd_accumulates(self) -> None:
        """gross_ytd closing equals opening plus period gross."""
        opening = PeriodState(gross_ytd=Decimal("10000.00"))
        result = calculate_period(_req(opening_state=opening))
        expected = Decimal("10000.00") + result.period_gross
        assert result.closing_state.gross_ytd == expected

    def test_inps_employee_ytd_accumulates(self) -> None:
        """inps_employee_ytd closing equals opening plus period employee INPS."""
        opening = PeriodState(inps_employee_ytd=Decimal("500.00"))
        result = calculate_period(_req(opening_state=opening))
        inps_period = sum(
            e.amount
            for e in result.ledger_entries
            if e.account == AccountKind.EMPLOYEE_CONTRIBUTIONS
        )
        assert result.closing_state.inps_employee_ytd == Decimal("500.00") + inps_period

    def test_remaining_months_guard_no_error(self) -> None:
        """months_closed == additional_months (13 for metalmeccanico) → remaining=1."""
        opening = PeriodState(months_closed=13)
        result = calculate_period(_req(opening_state=opening))
        assert result.period_gross > _ZERO


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


class TestTrattamentoPeriod:
    """_trattamento_period: None rules returns zero; eligible income returns >0."""

    def test_none_rules_returns_zero(self) -> None:
        """When ti_rules is None, _trattamento_period must return zero."""
        result = _trattamento_period(
            taxable=Decimal(10000),
            irpef_gross=Decimal(2300),
            work_ded=Decimal(1955),
            ti_rules=None,
            additional_months=13,
        )
        assert result == _ZERO

    def test_eligible_income_returns_positive(self) -> None:
        """Low-income + positive irpef_net → trattamento > 0."""
        ti_rules = TrattamentoIntegrativoRules(
            threshold_mid=Decimal(15000),
            threshold_upper=Decimal(28000),
            max_amount=Decimal(1200),
        )
        result = _trattamento_period(
            taxable=Decimal(10000),  # ≤ threshold_mid (15000)
            irpef_gross=Decimal(2300),  # > work_ded - 75 = 1880
            work_ded=Decimal(1955),
            ti_rules=ti_rules,
            additional_months=13,
        )
        assert result > _ZERO


class TestBuildPayItemsWithTrattamento:
    """_build_pay_items includes TaxCreditItem when period_tratt > 0."""

    def test_no_tax_credit_when_tratt_zero(self) -> None:
        """When period_tratt is zero, no TaxCreditItem is emitted."""
        period_id = PeriodId(year=2026, month=1)
        items = _build_pay_items(
            _amounts(period_tratt=_ZERO),
            period_id,
            date(2026, 1, 31),
        )
        assert not any(isinstance(i, TaxCreditItem) for i in items)

    def test_tax_credit_included_when_tratt_positive(self) -> None:
        """When period_tratt > 0, exactly one TaxCreditItem with correct amount."""
        period_id = PeriodId(year=2026, month=1)
        items = _build_pay_items(
            _amounts(period_tratt=Decimal("92.31")),
            period_id,
            date(2026, 1, 31),
        )
        credit_items = [i for i in items if isinstance(i, TaxCreditItem)]
        assert len(credit_items) == 1
        assert credit_items[0].amount == Decimal("92.31")

    def test_base_items_always_present(self) -> None:
        """Base, INPS, IRPEF, employer, and TFR items are always present."""
        period_id = PeriodId(year=2026, month=1)
        items = _build_pay_items(
            _amounts(period_tratt=_ZERO),
            period_id,
            date(2026, 1, 31),
        )
        assert any(isinstance(i, BaseSalaryEarning) for i in items)
        assert any(isinstance(i, EmployeeWithholdingItem) for i in items)
        assert any(isinstance(i, EmployerContributionItem) for i in items)
        assert any(isinstance(i, TfrAccrualItem) for i in items)


class TestProjectLedgerWithTrattamento:
    """_project_ledger includes CREDITS entry when period_tratt > 0."""

    def test_no_credits_entry_when_tratt_zero(self) -> None:
        """When period_tratt is zero, no CREDITS ledger entry is emitted."""
        period_id = PeriodId(year=2026, month=1)
        entries = _project_ledger(
            _amounts(period_tratt=_ZERO),
            period_id,
            date(2026, 1, 31),
        )
        accounts = [e.account for e in entries]
        assert AccountKind.CREDITS not in accounts

    def test_credits_entry_when_tratt_positive(self) -> None:
        """When period_tratt > 0, a CREDITS entry with correct amount is emitted."""
        period_id = PeriodId(year=2026, month=1)
        entries = _project_ledger(
            _amounts(period_tratt=Decimal("92.31")),
            period_id,
            date(2026, 1, 31),
        )
        credit_entries = [e for e in entries if e.account == AccountKind.CREDITS]
        assert len(credit_entries) == 1
        assert credit_entries[0].amount == Decimal("92.31")

    def test_base_accounts_always_present(self) -> None:
        """All five base ledger accounts are always emitted."""
        period_id = PeriodId(year=2026, month=1)
        entries = _project_ledger(
            _amounts(period_tratt=_ZERO),
            period_id,
            date(2026, 1, 31),
        )
        accounts = {e.account for e in entries}
        assert AccountKind.CASH_EARNINGS in accounts
        assert AccountKind.EMPLOYEE_CONTRIBUTIONS in accounts
        assert AccountKind.ORDINARY_TAX in accounts
        assert AccountKind.EMPLOYER_CONTRIBUTIONS in accounts
        assert AccountKind.TFR_ACCRUAL in accounts


class TestContractTypeRouting:
    """contract_type on PeriodCalculationRequest routes gross and INPS correctly."""

    def test_apprentice_gross_below_permanent(self) -> None:
        """Apprentice (85% track) produces a lower period_gross than Permanent."""
        permanent_req = PeriodCalculationRequest(
            period_id=PeriodId(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            opening_state=PeriodState.zero(),
        )
        # metalmeccanico track professionalizzante_36: months 0-12 → 85%
        # C3 is covered by two tracks; explicit track= is required.
        apprentice_req = PeriodCalculationRequest(
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
            period_id=PeriodId(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            opening_state=PeriodState.zero(),
        )
        fixed_req = PeriodCalculationRequest(
            period_id=PeriodId(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            opening_state=PeriodState.zero(),
            contract_type=FixedTerm(),
        )
        perm_result = calculate_period(permanent_req)
        fixed_result = calculate_period(fixed_req)
        assert fixed_result.period_gross == perm_result.period_gross


class TestEventDateValidation:
    """Events outside the competence period raise InvalidInputError."""

    def test_overtime_outside_period_raises(self) -> None:
        """OvertimeEvent with event_date outside period raises InvalidInputError."""
        out_of_period = OvertimeEvent(
            event_date=date(2026, 2, 10),  # February, not January
            hours=Decimal(8),
            hourly_rate=Decimal(20),
            multiplier=Decimal("1.25"),
        )
        req = PeriodCalculationRequest(
            period_id=PeriodId(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            opening_state=PeriodState.zero(),
            events=(out_of_period,),
        )
        with pytest.raises(InvalidInputError, match="outside period"):
            calculate_period(req)

    def test_arrears_event_outside_period_allowed(self) -> None:
        """ArrearsEvent may reference past periods without raising."""
        past_arrears = ArrearsEvent(
            event_date=date(2025, 12, 1),  # prior year
            amount=Decimal("500.00"),
            separate_tax_rate=Decimal("0.23"),
        )
        req = PeriodCalculationRequest(
            period_id=PeriodId(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            opening_state=PeriodState.zero(),
            events=(past_arrears,),
        )
        result = calculate_period(req)
        assert result.period_gross > _ZERO
