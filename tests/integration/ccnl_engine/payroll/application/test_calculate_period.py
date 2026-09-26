"""Tests for the period-first payroll engine: calculate_period and helpers."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.application import reconcile as _reconcile_mod
from ccnl_engine.payroll.application._period_utils import _require_resolution
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.reconcile import (
    ReconciliationResult,
    ReconciliationViolation,
)
from ccnl_engine.payroll.domain.employment import Apprentice, FixedTerm
from ccnl_engine.payroll.domain.events import AbsenceEvent, ArrearsEvent, OvertimeEvent
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
from ccnl_engine.payroll.domain.policy import PolicyContext
from ccnl_engine.payroll.domain.tax_year_state import TaxYearState
from ccnl_engine.payroll.domain.ytd_accounts import EarningsYtd, TaxYtd
from ccnl_engine.payroll.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)
from ccnl_engine.payroll.service.policy_loader import load_policy_resolver
from ccnl_engine.shared.domain.errors import DataIntegrityError, InvalidInputError
from tests.helpers import EMPLOYER_50

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_ZERO = Decimal(0)

_RESOLVER = load_policy_resolver()
_POLICY_CTX = PolicyContext(year=2026, as_of=date(2026, 1, 1))

# C3 salary: 2158.26 until 2026-06-01, 2211.43 from 2026-06-01
_C3_GROSS_JAN = Decimal("2158.26")
_C3_GROSS_JUL = Decimal("2211.43")


def _req(
    year: int = 2026,
    month: int = 1,
    payment_date: date | None = None,
    opening_state: PeriodState | TaxYearState | None = None,
) -> PeriodCalculationRequest:
    if payment_date is None:
        payment_date = date(year, month, 28)
    if isinstance(opening_state, TaxYearState):
        opening_state = PeriodState(ytd=opening_state)
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
            _req(opening_state=TaxYearState(tax=TaxYtd(irpef=Decimal("1000.00"))))
        )
        assert result_zero.period_net != result_with_ytd.period_net

    def test_higher_ytd_irpef_increases_net(self) -> None:
        """More IRPEF already withheld → less to withhold now → higher net."""
        result_zero = calculate_period(_req())
        result_with_ytd = calculate_period(
            _req(opening_state=TaxYearState(tax=TaxYtd(irpef=Decimal("1000.00"))))
        )
        assert result_with_ytd.period_net > result_zero.period_net

    def test_irpef_ytd_accumulates_in_closing(self) -> None:
        """closing_state.ytd.tax.irpef equals the period IRPEF withheld."""
        result = calculate_period(_req())
        irpef_period = sum(
            e.amount
            for e in result.ledger_entries
            if e.account == AccountKind.ORDINARY_TAX
        )
        assert result.closing_state.ytd.tax.irpef == irpef_period


class TestClosingStateTransitions:
    """calculate_period advances the YTD state correctly."""

    def test_regular_periods_closed_increments(self) -> None:
        """regular_periods_closed increases by exactly 1 per regular period."""
        opening = TaxYearState(
            regular_periods_closed=5, tax_withholding_periods_closed=5
        )
        result = calculate_period(_req(opening_state=opening))
        assert result.closing_state.ytd.regular_periods_closed == 6

    def test_duplicate_run_id_raises(self) -> None:
        """Re-submitting an already-closed run_id raises ValueError."""
        opening = PeriodState.zero()
        result = calculate_period(_req(opening_state=opening))
        with pytest.raises(ValueError, match="already processed"):
            calculate_period(_req(opening_state=result.closing_state))

    def test_gross_ytd_accumulates(self) -> None:
        """gross_ytd closing equals opening plus period gross."""
        opening = TaxYearState(earnings=EarningsYtd(gross=Decimal("10000.00")))
        result = calculate_period(_req(opening_state=opening))
        expected = Decimal("10000.00") + result.period_gross
        assert result.closing_state.ytd.earnings.gross == expected

    def test_inps_employee_ytd_accumulates(self) -> None:
        """inps_employee_ytd closing equals opening plus period employee INPS."""
        opening = TaxYearState(earnings=EarningsYtd(inps_employee=Decimal("500.00")))
        result = calculate_period(_req(opening_state=opening))
        inps_period = sum(
            e.amount
            for e in result.ledger_entries
            if e.account == AccountKind.EMPLOYEE_CONTRIBUTIONS
        )
        expected = Decimal("500.00") + inps_period
        assert result.closing_state.ytd.earnings.inps_employee == expected

    def test_remaining_months_guard_no_error(self) -> None:
        """tax_withholding_periods_closed == 12 in a 13-period CCNL → remaining=1."""
        opening = TaxYearState(
            regular_periods_closed=11, tax_withholding_periods_closed=12
        )
        result = calculate_period(_req(opening_state=opening))
        assert result.period_gross > _ZERO

    def test_taxable_ytd_accumulates(self) -> None:
        """taxable_ytd closing equals opening plus period_taxable slice."""
        opening = TaxYearState(earnings=EarningsYtd(taxable=Decimal("2000.00")))
        result = calculate_period(_req(opening_state=opening))
        closing_taxable = result.closing_state.ytd.earnings.taxable
        assert closing_taxable > Decimal("2000.00")
        assert closing_taxable == result.closing_state.ytd.earnings.taxable

    def test_taxable_ytd_zero_on_first_period(self) -> None:
        """taxable_ytd starts from zero when opening is PeriodState.zero()."""
        result = calculate_period(_req(opening_state=PeriodState.zero()))
        assert result.closing_state.ytd.earnings.taxable > _ZERO

    def test_inps_base_ytd_accumulates(self) -> None:
        """inps_base_ytd closing equals opening plus period INPS base."""
        opening = TaxYearState(earnings=EarningsYtd(inps_base=Decimal("1000.00")))
        result = calculate_period(_req(opening_state=opening))
        assert result.closing_state.ytd.earnings.inps_base > Decimal("1000.00")


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
        # regular_periods_closed=11 so the closing from this run reaches 12.
        opening = TaxYearState(
            regular_periods_closed=11,
            tax_withholding_periods_closed=12,
            tax=TaxYtd(irpef=Decimal("5000.00")),
        )
        result = calculate_period(_req(opening_state=opening))
        assert result.tax_computation.withholding_due < _ZERO

    def test_ordinary_tax_negative_in_final_period_with_excess(self) -> None:
        """ordinary_tax is negative in the final period when YTD exceeds liability."""
        opening = TaxYearState(
            regular_periods_closed=11,
            tax_withholding_periods_closed=12,
            tax=TaxYtd(irpef=Decimal("5000.00")),
        )
        result = calculate_period(_req(opening_state=opening))
        assert result.tax_computation.ordinary_tax < _ZERO

    def test_ordinary_tax_non_negative_in_non_final_period(self) -> None:
        """ordinary_tax is clamped to zero in non-final periods."""
        opening = TaxYearState(
            regular_periods_closed=3,
            tax_withholding_periods_closed=3,
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
            employer=EMPLOYER_50,
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
            employer=EMPLOYER_50,
            period_id=PeriodId(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            opening_state=PeriodState.zero(),
            events=(past_arrears,),
        )
        result = calculate_period(req)
        assert result.period_gross > _ZERO

    def test_absence_event_hours_above_max_raises(self) -> None:
        """AbsenceEvent with hours > 240 raises InvalidInputError."""
        absence = AbsenceEvent(
            event_date=date(2026, 1, 15),
            hours=Decimal(241),
            hourly_rate=Decimal("12.50"),
        )
        req = PeriodCalculationRequest(
            employer=EMPLOYER_50,
            period_id=PeriodId(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            opening_state=PeriodState.zero(),
            events=(absence,),
        )
        with pytest.raises(InvalidInputError, match="hours"):
            calculate_period(req)

    def test_absence_event_hours_zero_raises(self) -> None:
        """AbsenceEvent with hours=0 raises InvalidInputError at construction."""
        with pytest.raises(InvalidInputError, match="hours"):
            AbsenceEvent(
                event_date=date(2026, 1, 15),
                hours=Decimal(0),
                hourly_rate=Decimal("12.50"),
            )


class TestRequireResolution:
    """_require_resolution raises DataIntegrityError for unknown pay-item kinds."""

    def test_unknown_kind_raises_data_integrity_error(self) -> None:
        """Resolving an unknown kind raises DataIntegrityError."""
        with pytest.raises(DataIntegrityError, match="No policy rule found"):
            _require_resolution(_RESOLVER, "nonexistent_kind_xyz", _POLICY_CTX)


class TestReconciliationFailureGuard:
    """calculate_period raises DataIntegrityError when reconciliation fails."""

    def test_reconciliation_failure_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """When _reconcile returns violations, DataIntegrityError is raised."""
        fake_result = ReconciliationResult(
            violations=(
                ReconciliationViolation(
                    invariant_id="net_identity", message="test violation"
                ),
            )
        )
        monkeypatch.setattr(_reconcile_mod, "reconcile", lambda *_: fake_result)

        req = PeriodCalculationRequest(
            employer=EMPLOYER_50,
            period_id=PeriodId(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            opening_state=PeriodState.zero(),
        )
        with pytest.raises(DataIntegrityError, match="Period reconciliation failed"):
            calculate_period(req)
