"""Unit tests for ledger_builder.post_variable_pay."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.domain.ledger import AccountKind, Ledger, LedgerEntry
from ccnl_engine.engine.payroll.service.ledger_builder import post_variable_pay
from ccnl_engine.engine.payroll.service.work_rules import WorkRulesPay
from tests.unit.ccnl_engine.engine.payroll.service.builders import _DATE

_ZERO = Decimal(0)
_V = Decimal("100.00")


def _zero_work(**overrides: Decimal | bool) -> WorkRulesPay:
    """Build a WorkRulesPay with all zero/false values and optional overrides.

    Returns:
        A :class:`WorkRulesPay` suitable for testing individual fields.
    """
    base: dict[str, object] = {
        "base_monthly_full_time": _ZERO,
        "overtime_supp": _ZERO,
        "night_supp": _ZERO,
        "holiday_supp": _ZERO,
        "overtime_hours": _ZERO,
        "night_hours": _ZERO,
        "holiday_hours": _ZERO,
        "time_supplements_monthly": _ZERO,
        "time_supplements_annual_projection": _ZERO,
        "hourly_rate": _ZERO,
        "absence_deduction_monthly": _ZERO,
        "effective_gross_monthly": _ZERO,
        "leave_accrued_days_monthly": _ZERO,
        "leave_taken_days_monthly": _ZERO,
        "leave_balance_days": _ZERO,
        "sick_days_monthly": _ZERO,
        "sick_carenza_days_monthly": _ZERO,
        "sick_inps_indemnity_monthly": _ZERO,
        "sick_company_integration_monthly": _ZERO,
        "fringe_benefit_annual": _ZERO,
        "fringe_benefit_threshold_annual": _ZERO,
        "fringe_benefit_taxable_annual": _ZERO,
        "welfare_annual": _ZERO,
        "bonus_annual": _ZERO,
        "bonus_pdr_flat_tax_annual": _ZERO,
        "bonus_ordinary_taxable_annual": _ZERO,
        "bonus_pdr_missing_prior_year": False,
        "wr_overtime_supported": False,
        "wr_night_supported": False,
        "wr_holiday_supported": False,
        "wr_absence_present": False,
        "wr_leave_present": False,
        "wr_sickness_present": False,
        "supplement_trace": (),
        "warnings": (),
        "consumed_rulesets": {},
        "consumed_ruleset_ids": (),
        "consumed_verifications": {},
    }
    base.update(overrides)
    return WorkRulesPay(**base)  # type: ignore[arg-type]


def _post(work: WorkRulesPay) -> tuple[LedgerEntry, ...]:
    """Run post_variable_pay and return all ledger entries.

    Returns:
        Tuple of :class:`LedgerEntry` records appended by :func:`post_variable_pay`.
    """
    ledger = Ledger()
    post_variable_pay(work, _DATE, ledger)
    return ledger.entries()


class TestOvertimeSupplement:
    """post_variable_pay posts overtime_supp to GROSS_EARNINGS."""

    def test_overtime_entry_exists(self) -> None:
        """overtime_supplement entry is posted when overtime_supp is non-zero."""
        entries = _post(_zero_work(overtime_supp=_V))
        kinds = [e.pay_item_kind for e in entries]
        assert "overtime_supplement" in kinds

    def test_overtime_account(self) -> None:
        """overtime_supplement is posted to CASH_EARNINGS."""
        entries = _post(_zero_work(overtime_supp=_V))
        entry = next(e for e in entries if e.pay_item_kind == "overtime_supplement")
        assert entry.account == AccountKind.CASH_EARNINGS

    def test_overtime_amount(self) -> None:
        """overtime_supplement entry amount matches overtime_supp."""
        entries = _post(_zero_work(overtime_supp=_V))
        entry = next(e for e in entries if e.pay_item_kind == "overtime_supplement")
        assert entry.amount == _V

    def test_no_overtime_entry_when_zero(self) -> None:
        """No overtime_supplement when overtime_supp is zero."""
        entries = _post(_zero_work())
        kinds = [e.pay_item_kind for e in entries]
        assert "overtime_supplement" not in kinds

    def test_overtime_entry_id_format(self) -> None:
        """entry_id follows overtime_supplement_{year}_{month:02d} pattern."""
        entries = _post(_zero_work(overtime_supp=_V))
        entry = next(e for e in entries if e.pay_item_kind == "overtime_supplement")
        assert entry.entry_id == f"overtime_supplement_{_DATE.year}_{_DATE.month:02d}"


class TestNightSupplement:
    """post_variable_pay posts night_supp to GROSS_EARNINGS."""

    def test_night_entry_exists(self) -> None:
        """night_supplement entry is posted when night_supp is non-zero."""
        entries = _post(_zero_work(night_supp=_V))
        kinds = [e.pay_item_kind for e in entries]
        assert "night_supplement" in kinds

    def test_night_account(self) -> None:
        """night_supplement is posted to CASH_EARNINGS."""
        entries = _post(_zero_work(night_supp=_V))
        entry = next(e for e in entries if e.pay_item_kind == "night_supplement")
        assert entry.account == AccountKind.CASH_EARNINGS

    def test_no_night_entry_when_zero(self) -> None:
        """No night_supplement when night_supp is zero."""
        entries = _post(_zero_work())
        kinds = [e.pay_item_kind for e in entries]
        assert "night_supplement" not in kinds


class TestHolidaySupplement:
    """post_variable_pay posts holiday_supp to GROSS_EARNINGS."""

    def test_holiday_entry_exists(self) -> None:
        """holiday_supplement entry is posted when holiday_supp is non-zero."""
        entries = _post(_zero_work(holiday_supp=_V))
        kinds = [e.pay_item_kind for e in entries]
        assert "holiday_supplement" in kinds

    def test_holiday_account(self) -> None:
        """holiday_supplement is posted to CASH_EARNINGS."""
        entries = _post(_zero_work(holiday_supp=_V))
        entry = next(e for e in entries if e.pay_item_kind == "holiday_supplement")
        assert entry.account == AccountKind.CASH_EARNINGS

    def test_no_holiday_entry_when_zero(self) -> None:
        """No holiday_supplement when holiday_supp is zero."""
        entries = _post(_zero_work())
        kinds = [e.pay_item_kind for e in entries]
        assert "holiday_supplement" not in kinds


class TestAbsenceDeduction:
    """post_variable_pay posts absence_deduction as negative GROSS_EARNINGS."""

    def test_absence_entry_exists(self) -> None:
        """absence_deduction entry is posted when absence_deduction_monthly != 0."""
        entries = _post(_zero_work(absence_deduction_monthly=_V))
        kinds = [e.pay_item_kind for e in entries]
        assert "absence_deduction" in kinds

    def test_absence_account(self) -> None:
        """absence_deduction is posted to EMPLOYEE_DEDUCTIONS."""
        entries = _post(_zero_work(absence_deduction_monthly=_V))
        entry = next(e for e in entries if e.pay_item_kind == "absence_deduction")
        assert entry.account == AccountKind.EMPLOYEE_DEDUCTIONS

    def test_absence_amount_is_positive(self) -> None:
        """absence_deduction amount is positive in EMPLOYEE_DEDUCTIONS."""
        entries = _post(_zero_work(absence_deduction_monthly=_V))
        entry = next(e for e in entries if e.pay_item_kind == "absence_deduction")
        assert entry.amount == _V

    def test_no_absence_entry_when_zero(self) -> None:
        """No absence_deduction when absence_deduction_monthly is zero."""
        entries = _post(_zero_work())
        kinds = [e.pay_item_kind for e in entries]
        assert "absence_deduction" not in kinds

    def test_absence_entry_id_format(self) -> None:
        """entry_id follows absence_deduction_{year}_{month:02d} pattern."""
        entries = _post(_zero_work(absence_deduction_monthly=_V))
        entry = next(e for e in entries if e.pay_item_kind == "absence_deduction")
        assert entry.entry_id == f"absence_deduction_{_DATE.year}_{_DATE.month:02d}"


class TestBonus:
    """post_variable_pay posts bonus_annual to GROSS_EARNINGS."""

    def test_bonus_entry_exists(self) -> None:
        """Bonus entry is posted when bonus_annual is non-zero."""
        entries = _post(_zero_work(bonus_annual=_V))
        kinds = [e.pay_item_kind for e in entries]
        assert "bonus" in kinds

    def test_bonus_account(self) -> None:
        """Bonus is posted to CASH_EARNINGS."""
        entries = _post(_zero_work(bonus_annual=_V))
        entry = next(e for e in entries if e.pay_item_kind == "bonus")
        assert entry.account == AccountKind.CASH_EARNINGS

    def test_bonus_amount(self) -> None:
        """Bonus entry amount matches bonus_annual."""
        entries = _post(_zero_work(bonus_annual=_V))
        entry = next(e for e in entries if e.pay_item_kind == "bonus")
        assert entry.amount == _V

    def test_no_bonus_entry_when_zero(self) -> None:
        """No bonus when bonus_annual is zero."""
        entries = _post(_zero_work())
        kinds = [e.pay_item_kind for e in entries]
        assert "bonus" not in kinds

    def test_bonus_entry_id_format(self) -> None:
        """entry_id follows bonus_{year}_{month:02d} pattern."""
        entries = _post(_zero_work(bonus_annual=_V))
        entry = next(e for e in entries if e.pay_item_kind == "bonus")
        assert entry.entry_id == f"bonus_{_DATE.year}_{_DATE.month:02d}"


class TestFringeBenefitTaxable:
    """post_variable_pay posts fringe_benefit_taxable_annual to GROSS_EARNINGS."""

    def test_fringe_entry_exists(self) -> None:
        """fringe_benefit_taxable entry is posted when taxable fringe is non-zero."""
        entries = _post(_zero_work(fringe_benefit_taxable_annual=_V))
        kinds = [e.pay_item_kind for e in entries]
        assert "fringe_benefit_taxable" in kinds

    def test_fringe_account(self) -> None:
        """fringe_benefit_taxable is posted to NON_CASH_BENEFITS."""
        entries = _post(_zero_work(fringe_benefit_taxable_annual=_V))
        entry = next(e for e in entries if e.pay_item_kind == "fringe_benefit_taxable")
        assert entry.account == AccountKind.NON_CASH_BENEFITS

    def test_fringe_amount(self) -> None:
        """fringe_benefit_taxable amount matches fringe_benefit_taxable_annual."""
        entries = _post(_zero_work(fringe_benefit_taxable_annual=_V))
        entry = next(e for e in entries if e.pay_item_kind == "fringe_benefit_taxable")
        assert entry.amount == _V

    def test_no_fringe_entry_when_zero(self) -> None:
        """No fringe_benefit_taxable when fringe_benefit_taxable_annual is zero."""
        entries = _post(_zero_work())
        kinds = [e.pay_item_kind for e in entries]
        assert "fringe_benefit_taxable" not in kinds


class TestWelfare:
    """post_variable_pay posts welfare_annual to NON_CASH_BENEFITS."""

    def test_welfare_entry_exists(self) -> None:
        """Welfare entry is posted when welfare_annual is non-zero."""
        entries = _post(_zero_work(welfare_annual=_V))
        kinds = [e.pay_item_kind for e in entries]
        assert "welfare" in kinds

    def test_welfare_account(self) -> None:
        """Welfare is posted to NON_CASH_BENEFITS."""
        entries = _post(_zero_work(welfare_annual=_V))
        entry = next(e for e in entries if e.pay_item_kind == "welfare")
        assert entry.account == AccountKind.NON_CASH_BENEFITS

    def test_welfare_amount(self) -> None:
        """Welfare entry amount matches welfare_annual."""
        entries = _post(_zero_work(welfare_annual=_V))
        entry = next(e for e in entries if e.pay_item_kind == "welfare")
        assert entry.amount == _V

    def test_no_welfare_entry_when_zero(self) -> None:
        """No welfare entry when welfare_annual is zero."""
        entries = _post(_zero_work())
        kinds = [e.pay_item_kind for e in entries]
        assert "welfare" not in kinds


class TestZeroAmountsSkipped:
    """post_variable_pay produces no entries when all variable pay is zero."""

    def test_all_zero_produces_empty_ledger(self) -> None:
        """All-zero WorkRulesPay produces no ledger entries."""
        entries = _post(_zero_work())
        assert entries == ()


class TestCompetencePeriod:
    """All variable pay entries carry the correct competence period."""

    @pytest.mark.parametrize(
        "field",
        [
            "overtime_supp",
            "night_supp",
            "holiday_supp",
            "bonus_annual",
            "fringe_benefit_taxable_annual",
            "welfare_annual",
            "absence_deduction_monthly",
        ],
    )
    def test_competence_period_matches_as_of(self, field: str) -> None:
        """Each entry's competence period matches the as_of date."""
        entries = _post(_zero_work(**{field: _V}))
        assert len(entries) == 1
        assert entries[0].competence_period.year == _DATE.year
        assert entries[0].competence_period.month == _DATE.month


class TestEntryCount:
    """Number of entries reflects non-zero variable pay components."""

    def test_all_variable_components_produce_seven_entries(self) -> None:
        """All seven posted components yield seven ledger entries."""
        work = _zero_work(
            overtime_supp=_V,
            night_supp=_V,
            holiday_supp=_V,
            absence_deduction_monthly=_V,
            bonus_annual=_V,
            fringe_benefit_taxable_annual=_V,
            welfare_annual=_V,
        )
        entries = _post(work)
        assert len(entries) == 7

    @pytest.mark.parametrize(
        ("field", "count"),
        [
            ("overtime_supp", 1),
            ("night_supp", 1),
            ("holiday_supp", 1),
            ("absence_deduction_monthly", 1),
            ("bonus_annual", 1),
            ("fringe_benefit_taxable_annual", 1),
            ("welfare_annual", 1),
        ],
    )
    def test_single_component_yields_one_entry(self, field: str, count: int) -> None:
        """Each individual component produces exactly one entry."""
        entries = _post(_zero_work(**{field: _V}))
        assert len(entries) == count
