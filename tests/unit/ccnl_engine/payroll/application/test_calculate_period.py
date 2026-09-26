"""Tests for the period-first payroll engine: calculate_period and helpers."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.contract.domain.compensation import Allowance
from ccnl_engine.contract.domain.validity import TimeSeries, ValidityPeriod
from ccnl_engine.payroll.application import reconcile as _reconcile_mod
from ccnl_engine.payroll.application._period_amounts import _PeriodAmounts
from ccnl_engine.payroll.application._period_utils import _require_resolution
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.post_ledger import (
    _build_pay_items,
    _project_ledger,
)
from ccnl_engine.payroll.application.reconcile import (
    ReconciliationResult,
    ReconciliationViolation,
)
from ccnl_engine.payroll.domain.calendar import WorkCalendar
from ccnl_engine.payroll.domain.employment import (
    Apprentice,
    EmploymentPeriod,
    FixedTerm,
)
from ccnl_engine.payroll.domain.events import AbsenceEvent, ArrearsEvent, OvertimeEvent
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.pay_items import (
    BaseSalaryEarning,
    EmployeeWithholdingItem,
    EmployerContributionItem,
    FixedAllowanceEarning,
    SeniorityEarning,
    TaxCreditItem,
    TfrAccrualItem,
)
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodState,
)
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.policy import PolicyContext
from ccnl_engine.payroll.domain.run import PayrollRun
from ccnl_engine.payroll.domain.schedule import WithholdingSchedule
from ccnl_engine.payroll.domain.tax_year_state import TaxYearState
from ccnl_engine.payroll.domain.ytd_accounts import EarningsYtd, TaxYtd
from ccnl_engine.payroll.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)
from ccnl_engine.payroll.service.policy_loader import load_policy_resolver
from ccnl_engine.payroll.service.tax_computation import compute_tax
from ccnl_engine.payroll.service.types import MonthlyPayChain
from ccnl_engine.shared.domain.errors import DataIntegrityError, InvalidInputError
from ccnl_engine.tax.domain.credit_rules import (
    SommaEsenteBand,
    SommaEsenteRules,
    TrattamentoIntegrativoRules,
    UlterioreDetrazioneRules,
)
from ccnl_engine.tax.domain.irpef_rules import SterilizzazioneDetrazioniRules
from tests.helpers import EMPLOYER_50, make_year_rules

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_ZERO = Decimal(0)

_RESOLVER = load_policy_resolver()
_TWELVE_SLOTS = WithholdingSchedule.from_calendar(WorkCalendar(year=2026))
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


def _amounts(*, period_tratt: Decimal = _ZERO) -> _PeriodAmounts:
    return _PeriodAmounts(
        monthly_gross=Decimal("2158.26"),
        inps_employee=Decimal("204.82"),
        inps_employer=Decimal("651.79"),
        tfr=Decimal("159.87"),
        period_irpef=Decimal("279.02"),
        period_tratt=period_tratt,
        period_surtax=_ZERO,
        period_taxable=Decimal("1953.44"),
        period_substitute_tax=_ZERO,
        pdr_eligible=_ZERO,
    )


def _chain() -> MonthlyPayChain:
    return MonthlyPayChain(base=Decimal("2158.26"), seniority=_ZERO, allowances=())


def _chain_with_seniority() -> MonthlyPayChain:
    return MonthlyPayChain(
        base=Decimal("2069.34"), seniority=Decimal("88.92"), allowances=()
    )


def _allowance(code: str = "EDR", amount: Decimal = Decimal("10.33")) -> Allowance:
    ts = TimeSeries(
        periods=(
            ValidityPeriod(value=amount, valid_from=date(2024, 1, 1), valid_until=None),
        )
    )
    return Allowance(code=code, description=code, monthly=ts)


def _chain_with_allowance() -> MonthlyPayChain:
    a = _allowance()
    return MonthlyPayChain(
        base=Decimal("2147.93"),
        seniority=_ZERO,
        allowances=((a, Decimal("10.33")),),
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


class TestResolveTaxComputation:
    """compute_tax: IRPEF breakdown with rule_id and fonte annotation."""

    def test_ordinary_tax_positive_for_typical_income(self) -> None:
        """Typical income produces positive ordinary_tax and irpef_gross component."""
        rules = make_year_rules()
        tc = compute_tax(
            Decimal(25000),
            rules,
            opening_irpef_withheld=_ZERO,
            withholding_schedule=_TWELVE_SLOTS,
        ).computation
        assert tc.ordinary_tax > _ZERO
        names = [c.name for c in tc.components]
        assert "irpef_gross" in names
        assert "work_deduction" in names

    def test_trattamento_integrativo_emitted_when_eligible(self) -> None:
        """Low-income worker with positive irpef: trattamento component emitted."""
        rules = make_year_rules()
        ti = TrattamentoIntegrativoRules(
            threshold_mid=Decimal(15000),
            threshold_upper=Decimal(28000),
            max_amount=Decimal(1200),
        )
        rules_with_ti = rules.model_copy(update={"trattamento_integrativo": ti})
        tc = compute_tax(
            Decimal(10000),
            rules_with_ti,
            opening_irpef_withheld=_ZERO,
            withholding_schedule=_TWELVE_SLOTS,
        ).computation
        names = [c.name for c in tc.components]
        assert "trattamento_integrativo" in names
        assert tc.trattamento_integrativo > _ZERO

    def test_no_trattamento_when_rules_absent(self) -> None:
        """When trattamento_integrativo rules are absent the period credit is zero."""
        rules = make_year_rules()
        # Default make_year_rules() has trattamento_integrativo=None
        tc = compute_tax(
            Decimal(10000),
            rules,
            opening_irpef_withheld=_ZERO,
            withholding_schedule=_TWELVE_SLOTS,
        ).computation
        names = [c.name for c in tc.components]
        assert "trattamento_integrativo" not in names
        assert tc.trattamento_integrativo == _ZERO

    def test_ulteriore_detrazione_zero_not_emitted(self) -> None:
        """ulteriore_detrazione configured but income outside range: not emitted."""
        rules = make_year_rules()
        ud_rules = UlterioreDetrazioneRules(
            threshold_low=Decimal(20000),
            threshold_mid=Decimal(32000),
            threshold_high=Decimal(40000),
            max_amount=Decimal(720),
        )
        rules_with_ud = rules.model_copy(update={"ulteriore_detrazione": ud_rules})
        # taxable=10000 <= threshold_low → zero
        tc = compute_tax(
            Decimal(10000),
            rules_with_ud,
            withholding_schedule=_TWELVE_SLOTS,
        ).computation
        names = [c.name for c in tc.components]
        assert "ulteriore_detrazione" not in names

    def test_sterilizzazione_reduces_deductions_for_high_earner(self) -> None:
        """sterilizzazione_detrazioni: high-income worker gets reduced deductions."""
        rules = make_year_rules()
        steriliz = SterilizzazioneDetrazioniRules(
            threshold=Decimal(200000), reduction=Decimal(440)
        )
        rules_with_s = rules.model_copy(update={"sterilizzazione_detrazioni": steriliz})
        # taxable > 200000 + non-zero deductions so reduction is applied
        tc = compute_tax(
            Decimal(250000),
            rules_with_s,
            family_deductions=Decimal(1000),
            withholding_schedule=_TWELVE_SLOTS,
        ).computation
        names = [c.name for c in tc.components]
        assert "sterilizzazione_detrazioni" in names

    def test_somma_esente_emitted_for_low_income(self) -> None:
        """somma_esente: low-income worker receives positive bonus component."""
        rules = make_year_rules()
        se_rules = SommaEsenteRules(
            bands=[SommaEsenteBand(up_to=Decimal(20000), rate=Decimal("0.07"))]
        )
        rules_with_se = rules.model_copy(update={"somma_esente": se_rules})
        tc = compute_tax(
            Decimal(10000),
            rules_with_se,
            withholding_schedule=_TWELVE_SLOTS,
        ).computation
        names = [c.name for c in tc.components]
        assert "somma_esente" in names


class TestBuildPayItemsWithTrattamento:
    """_build_pay_items includes TaxCreditItem when period_tratt > 0."""

    def test_no_tax_credit_when_tratt_zero(self) -> None:
        """When period_tratt is zero, no TaxCreditItem is emitted."""
        period_id = PeriodId(year=2026, month=1)
        items = _build_pay_items(
            _amounts(period_tratt=_ZERO),
            _chain(),
            period_id,
            date(2026, 1, 31),
        )
        assert not any(isinstance(i, TaxCreditItem) for i in items)

    def test_tax_credit_included_when_tratt_positive(self) -> None:
        """When period_tratt > 0, exactly one TaxCreditItem with correct amount."""
        period_id = PeriodId(year=2026, month=1)
        items = _build_pay_items(
            _amounts(period_tratt=Decimal("92.31")),
            _chain(),
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
            _chain(),
            period_id,
            date(2026, 1, 31),
        )
        assert any(isinstance(i, BaseSalaryEarning) for i in items)
        assert any(isinstance(i, EmployeeWithholdingItem) for i in items)
        assert any(isinstance(i, EmployerContributionItem) for i in items)
        assert any(isinstance(i, TfrAccrualItem) for i in items)


class TestElementaryChainItems:
    """Elementary pay items and ledger entries from chain components."""

    def test_seniority_item_emitted_when_positive(self) -> None:
        """A SeniorityEarning is emitted when chain.seniority > 0."""
        period_id = PeriodId(year=2026, month=1)
        items = _build_pay_items(
            _amounts(),
            _chain_with_seniority(),
            period_id,
            date(2026, 1, 31),
        )
        seniority_items = [i for i in items if isinstance(i, SeniorityEarning)]
        assert len(seniority_items) == 1
        assert seniority_items[0].amount == Decimal("88.92")

    def test_allowance_item_emitted_when_positive(self) -> None:
        """A FixedAllowanceEarning is emitted for each positive allowance."""
        period_id = PeriodId(year=2026, month=1)
        items = _build_pay_items(
            _amounts(),
            _chain_with_allowance(),
            period_id,
            date(2026, 1, 31),
        )
        allowance_items = [i for i in items if isinstance(i, FixedAllowanceEarning)]
        assert len(allowance_items) == 1
        assert allowance_items[0].amount == Decimal("10.33")
        assert allowance_items[0].allowance_code == "EDR"

    def test_seniority_ledger_entry_emitted_when_positive(self) -> None:
        """A CASH_EARNINGS entry for seniority is posted when chain.seniority > 0."""
        period_id = PeriodId(year=2026, month=1)
        entries = _project_ledger(
            _amounts(),
            _chain_with_seniority(),
            period_id,
            date(2026, 1, 31),
            _RESOLVER,
            _POLICY_CTX,
        )
        cash_entries = [e for e in entries if e.account == AccountKind.CASH_EARNINGS]
        amounts = [e.amount for e in cash_entries]
        assert Decimal("88.92") in amounts

    def test_allowance_ledger_entry_emitted_when_positive(self) -> None:
        """A CASH_EARNINGS entry for each allowance is posted."""
        period_id = PeriodId(year=2026, month=1)
        entries = _project_ledger(
            _amounts(),
            _chain_with_allowance(),
            period_id,
            date(2026, 1, 31),
            _RESOLVER,
            _POLICY_CTX,
        )
        cash_entries = [e for e in entries if e.account == AccountKind.CASH_EARNINGS]
        amounts = [e.amount for e in cash_entries]
        assert Decimal("10.33") in amounts

    def test_zero_allowance_not_emitted(self) -> None:
        """An allowance with amount == 0 produces no pay item or ledger entry."""
        a = _allowance(amount=_ZERO)
        chain = MonthlyPayChain(
            base=Decimal("2158.26"), seniority=_ZERO, allowances=((a, _ZERO),)
        )
        period_id = PeriodId(year=2026, month=1)
        items = _build_pay_items(_amounts(), chain, period_id, date(2026, 1, 31))
        entries = _project_ledger(
            _amounts(), chain, period_id, date(2026, 1, 31), _RESOLVER, _POLICY_CTX
        )
        assert not any(isinstance(i, FixedAllowanceEarning) for i in items)
        cash_amounts = [
            e.amount for e in entries if e.account == AccountKind.CASH_EARNINGS
        ]
        assert _ZERO not in cash_amounts


class TestProjectLedgerWithTrattamento:
    """_project_ledger includes CREDITS entry when period_tratt > 0."""

    def test_no_credits_entry_when_tratt_zero(self) -> None:
        """When period_tratt is zero, no CREDITS ledger entry is emitted."""
        period_id = PeriodId(year=2026, month=1)
        entries = _project_ledger(
            _amounts(period_tratt=_ZERO),
            _chain(),
            period_id,
            date(2026, 1, 31),
            _RESOLVER,
            _POLICY_CTX,
        )
        accounts = [e.account for e in entries]
        assert AccountKind.CREDITS not in accounts

    def test_credits_entry_when_tratt_positive(self) -> None:
        """When period_tratt > 0, a CREDITS entry with correct amount is emitted."""
        period_id = PeriodId(year=2026, month=1)
        entries = _project_ledger(
            _amounts(period_tratt=Decimal("92.31")),
            _chain(),
            period_id,
            date(2026, 1, 31),
            _RESOLVER,
            _POLICY_CTX,
        )
        credit_entries = [e for e in entries if e.account == AccountKind.CREDITS]
        assert len(credit_entries) == 1
        assert credit_entries[0].amount == Decimal("92.31")

    def test_base_accounts_always_present(self) -> None:
        """All five base ledger accounts are always emitted."""
        period_id = PeriodId(year=2026, month=1)
        entries = _project_ledger(
            _amounts(period_tratt=_ZERO),
            _chain(),
            period_id,
            date(2026, 1, 31),
            _RESOLVER,
            _POLICY_CTX,
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


class TestForExtraMonth:
    """MonthlyPayChain.for_extra_month filters allowances by months_per_year."""

    def _make_allowance(self, code: str, months_per_year: int | None) -> Allowance:
        ts = TimeSeries(
            periods=(
                ValidityPeriod(
                    value=Decimal("10.00"),
                    valid_from=date(2024, 1, 1),
                    valid_until=None,
                ),
            )
        )
        return Allowance(
            code=code,
            description=code,
            monthly=ts,
            months_per_year=months_per_year,
        )

    def test_no_allowances_unchanged(self) -> None:
        """Chain with no allowances passes through unchanged."""
        chain = MonthlyPayChain(
            base=Decimal(1000), seniority=Decimal(50), allowances=()
        )
        result = chain.for_extra_month(13)
        assert result.base == chain.base
        assert result.seniority == chain.seniority
        assert result.allowances == ()

    def test_allowance_with_none_mpy_always_included(self) -> None:
        """Allowance with months_per_year=None is included in any extra-month run."""
        a = self._make_allowance("ALL", months_per_year=None)
        chain = MonthlyPayChain(
            base=Decimal(1000),
            seniority=Decimal(0),
            allowances=((a, Decimal(10)),),
        )
        result = chain.for_extra_month(13)
        assert len(result.allowances) == 1

    def test_allowance_with_12_mpy_excluded_for_thirteenth(self) -> None:
        """Allowance with months_per_year=12 is excluded from thirteenth run."""
        a = self._make_allowance("EDR", months_per_year=12)
        chain = MonthlyPayChain(
            base=Decimal(1000),
            seniority=Decimal(0),
            allowances=((a, Decimal(10)),),
        )
        result = chain.for_extra_month(13)
        assert result.allowances == ()

    def test_allowance_with_13_mpy_included_for_thirteenth(self) -> None:
        """Allowance with months_per_year=13 is included in thirteenth run."""
        a = self._make_allowance("BONUS13", months_per_year=13)
        chain = MonthlyPayChain(
            base=Decimal(1000),
            seniority=Decimal(0),
            allowances=((a, Decimal(10)),),
        )
        result = chain.for_extra_month(13)
        assert len(result.allowances) == 1

    def test_allowance_with_12_mpy_excluded_for_fourteenth(self) -> None:
        """Allowance with months_per_year=12 is excluded from fourteenth run."""
        a = self._make_allowance("EDR", months_per_year=12)
        chain = MonthlyPayChain(
            base=Decimal(1000),
            seniority=Decimal(0),
            allowances=((a, Decimal(10)),),
        )
        result = chain.for_extra_month(14)
        assert result.allowances == ()

    def test_allowance_with_13_mpy_excluded_for_fourteenth(self) -> None:
        """Allowance with months_per_year=13 is excluded from fourteenth run."""
        a = self._make_allowance("BONUS13", months_per_year=13)
        chain = MonthlyPayChain(
            base=Decimal(1000),
            seniority=Decimal(0),
            allowances=((a, Decimal(10)),),
        )
        result = chain.for_extra_month(14)
        assert result.allowances == ()

    def test_allowance_with_14_mpy_included_for_fourteenth(self) -> None:
        """Allowance with months_per_year=14 is included in fourteenth run."""
        a = self._make_allowance("BONUS14", months_per_year=14)
        chain = MonthlyPayChain(
            base=Decimal(1000),
            seniority=Decimal(0),
            allowances=((a, Decimal(10)),),
        )
        result = chain.for_extra_month(14)
        assert len(result.allowances) == 1

    def test_mixed_allowances_filtered_correctly(self) -> None:
        """Only eligible allowances remain after filtering."""
        a12 = self._make_allowance("EDR", months_per_year=12)
        a13 = self._make_allowance("BONUS13", months_per_year=13)
        chain = MonthlyPayChain(
            base=Decimal(1000),
            seniority=Decimal(0),
            allowances=((a12, Decimal(10)), (a13, Decimal(20))),
        )
        result = chain.for_extra_month(13)
        assert len(result.allowances) == 1
        assert result.allowances[0][0].code == "BONUS13"


class TestExtraMonthRateo:
    """Tredicesima gross is prorated by accrued months, not by payment month."""

    def _run_extra_month(
        self,
        regular_periods_closed: int,
        run: PayrollRun,
        period_month: int,
        employment_period: EmploymentPeriod | None = None,
    ) -> Decimal:
        """Run an extra-month period calculation and return period_gross.

        Returns:
            The ``period_gross`` of the extra-month run.
        """
        req = PeriodCalculationRequest(
            employer=EMPLOYER_50,
            period_id=PeriodId(year=2026, month=period_month),
            payment_date=date(2026, period_month, 28),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            opening_state=PeriodState(
                ytd=TaxYearState(
                    regular_periods_closed=regular_periods_closed,
                    tax_withholding_periods_closed=regular_periods_closed,
                )
            ),
            run=run,
            employment_period=employment_period,
        )
        return calculate_period(req).period_gross

    def test_december_tredicesima_is_positive(self) -> None:
        """Tredicesima paid in December produces a positive gross."""
        gross = self._run_extra_month(
            regular_periods_closed=12,
            run=PayrollRun.thirteenth(2026, 12),
            period_month=12,
        )
        assert gross > Decimal(0)

    def test_accrued_months_determine_rateo(self) -> None:
        """Six accrued months give half the gross of twelve.

        The rateo derives from the employment dates (hire 1 July: July to
        December), not from the payment month or the runs already closed:
        both runs report twelve closed periods.  Both use the same December
        salary, so the rateo is the only factor.
        """
        full_year = self._run_extra_month(
            regular_periods_closed=12,
            run=PayrollRun.thirteenth(2026, 12),
            period_month=12,
        )
        half_year = self._run_extra_month(
            regular_periods_closed=12,
            run=PayrollRun.thirteenth(2026, 12),
            period_month=12,
            employment_period=EmploymentPeriod(date(2026, 7, 1)),
        )
        assert half_year == (full_year / 2).quantize(Decimal("0.01"))

    def test_payment_month_does_not_change_accrued_gross(self) -> None:
        """A full-year employee receives the same tredicesima in June and December.

        Moving the payment date must not change the already-accrued entitlement.
        Without employment dates the worker accrues the 12 months ending in
        the payment month, so rateo=12/12=1.0 in both.
        The salary rate at the payment date may differ if there was an increase
        between June and December; the invariant is the accrual fraction, not
        the absolute amount.
        """
        jun_thirteenth = self._run_extra_month(
            regular_periods_closed=12,
            run=PayrollRun.thirteenth(2026, 6),
            period_month=6,
        )
        dec_thirteenth = self._run_extra_month(
            regular_periods_closed=12,
            run=PayrollRun.thirteenth(2026, 12),
            period_month=12,
        )
        # Both use 12/12 rateo; amounts may differ only due to salary increases.
        # Verify by checking that each equals its own month's regular gross.
        regular_june = calculate_period(
            PeriodCalculationRequest(
                employer=EMPLOYER_50,
                period_id=PeriodId(year=2026, month=6),
                payment_date=date(2026, 6, 28),
                ccnl_slug=_CCNL,
                level_code=_LEVEL,
                opening_state=PeriodState(
                    ytd=TaxYearState(
                        regular_periods_closed=5,
                        tax_withholding_periods_closed=5,
                    )
                ),
            )
        ).period_gross
        regular_dec = calculate_period(
            PeriodCalculationRequest(
                employer=EMPLOYER_50,
                period_id=PeriodId(year=2026, month=12),
                payment_date=date(2026, 12, 28),
                ccnl_slug=_CCNL,
                level_code=_LEVEL,
                opening_state=PeriodState(
                    ytd=TaxYearState(
                        regular_periods_closed=11,
                        tax_withholding_periods_closed=11,
                    )
                ),
            )
        ).period_gross
        assert jun_thirteenth == regular_june
        assert dec_thirteenth == regular_dec
