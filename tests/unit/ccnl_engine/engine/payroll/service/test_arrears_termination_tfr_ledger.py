"""Unit tests for ledger_builder.post_arrears_termination_tfr."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.domain.ledger import AccountKind, Ledger, LedgerEntry
from ccnl_engine.engine.payroll.service.fiscal import FiscalPay
from ccnl_engine.engine.payroll.service.ledger_builder import (
    post_arrears_termination_tfr,
)
from tests.unit.ccnl_engine.engine.payroll.service.builders import _DATE

_ZERO = Decimal(0)
_V = Decimal("100.00")

_KIND_ARREARS = "contract_renewal_arrears"
_KIND_LEAVE_PAYOUT = "termination_leave_payout"
_KIND_TFR_LIQ = "tfr_liquidation"
_KIND_TFR_ACCRUAL = "tfr_accrual"


def _zero_fiscal(**overrides: Decimal | bool | frozenset[object]) -> FiscalPay:
    """Build a FiscalPay with all monetary fields zeroed and optional overrides.

    Returns:
        A :class:`FiscalPay` suitable for testing individual fields.
    """
    base: dict[str, object] = {
        "consumed_ruleset_ids": (),
        "consumed_verifications": {},
        "inps_employee_annual": _ZERO,
        "inps_employer_annual": _ZERO,
        "inps_employee_additional_annual": _ZERO,
        "inail_employer_annual": _ZERO,
        "inps_employer_exemption_annual": _ZERO,
        "maternity_inps_indemnity_annual": _ZERO,
        "workplace_injury_inail_indemnity_annual": _ZERO,
        "termination_tfr_liquidation_annual": _ZERO,
        "employer_funds_annual": _ZERO,
        "tfr_annual": _ZERO,
        "bilateral_employee_annual": _ZERO,
        "bilateral_employer_annual": _ZERO,
        "taxable_income": _ZERO,
        "irpef_gross": _ZERO,
        "work_income_deduction": _ZERO,
        "fam_spouse": _ZERO,
        "fam_children": _ZERO,
        "fam_other": _ZERO,
        "fam_total": _ZERO,
        "fam_unused": _ZERO,
        "art15_total": _ZERO,
        "art15_unused": _ZERO,
        "sterilizzazione_clawback": _ZERO,
        "ulteriore_detrazione_lavoro": _ZERO,
        "somma_esente": _ZERO,
        "irpef_net": _ZERO,
        "conguaglio_annual": _ZERO,
        "termination_residual_leave_payout_annual": _ZERO,
        "contract_renewal_arrears_annual": _ZERO,
        "una_tantum_annual": _ZERO,
        "personal_withholdings_annual": _ZERO,
        "additional_irpef_base_annual": _ZERO,
        "health_fund_employee_annual": _ZERO,
        "health_fund_employer_annual": _ZERO,
        "territorial_supplement_annual": _ZERO,
        "company_supplement_annual": _ZERO,
        "trattamento_integrativo": _ZERO,
        "addizionale_regionale": _ZERO,
        "addizionale_comunale": _ZERO,
        "net_annual": _ZERO,
        "net_monthly": _ZERO,
        "employer_cost_annual": _ZERO,
        "employer_withholds_irpef": False,
        "fiscal_simplifications": frozenset(),
    }
    base.update(overrides)
    return FiscalPay(**base)  # type: ignore[arg-type]


def _post(fiscal: FiscalPay) -> tuple[LedgerEntry, ...]:
    """Run post_arrears_termination_tfr and return all ledger entries.

    Returns:
        Tuple of :class:`LedgerEntry` records appended by
        :func:`post_arrears_termination_tfr`.
    """
    ledger = Ledger()
    post_arrears_termination_tfr(fiscal, _DATE, ledger)
    return ledger.entries()


class TestContractRenewalArrears:
    """post_arrears_termination_tfr posts contract_renewal_arrears to GROSS_EARNINGS."""

    def test_arrears_entry_exists(self) -> None:
        """contract_renewal_arrears entry posted when amount is non-zero."""
        entries = _post(_zero_fiscal(contract_renewal_arrears_annual=_V))
        kinds = [e.pay_item_kind for e in entries]
        assert _KIND_ARREARS in kinds

    def test_arrears_account(self) -> None:
        """contract_renewal_arrears is posted to GROSS_EARNINGS."""
        entries = _post(_zero_fiscal(contract_renewal_arrears_annual=_V))
        entry = next(e for e in entries if e.pay_item_kind == _KIND_ARREARS)
        assert entry.account == AccountKind.GROSS_EARNINGS

    def test_arrears_amount(self) -> None:
        """contract_renewal_arrears amount matches contract_renewal_arrears_annual."""
        entries = _post(_zero_fiscal(contract_renewal_arrears_annual=_V))
        entry = next(e for e in entries if e.pay_item_kind == _KIND_ARREARS)
        assert entry.amount == _V

    def test_no_arrears_entry_when_zero(self) -> None:
        """No contract_renewal_arrears when contract_renewal_arrears_annual is zero."""
        entries = _post(_zero_fiscal())
        kinds = [e.pay_item_kind for e in entries]
        assert _KIND_ARREARS not in kinds

    def test_arrears_entry_id_format(self) -> None:
        """entry_id follows contract_renewal_arrears_{year}_{month:02d} pattern."""
        entries = _post(_zero_fiscal(contract_renewal_arrears_annual=_V))
        entry = next(e for e in entries if e.pay_item_kind == _KIND_ARREARS)
        expected = f"contract_renewal_arrears_{_DATE.year}_{_DATE.month:02d}"
        assert entry.entry_id == expected


class TestTerminationLeavePayout:
    """post_arrears_termination_tfr posts termination leave payout to GROSS_EARNINGS."""

    def test_leave_payout_entry_exists(self) -> None:
        """termination_leave_payout entry posted when amount is non-zero."""
        entries = _post(_zero_fiscal(termination_residual_leave_payout_annual=_V))
        kinds = [e.pay_item_kind for e in entries]
        assert _KIND_LEAVE_PAYOUT in kinds

    def test_leave_payout_account(self) -> None:
        """termination_leave_payout is posted to GROSS_EARNINGS."""
        entries = _post(_zero_fiscal(termination_residual_leave_payout_annual=_V))
        entry = next(e for e in entries if e.pay_item_kind == _KIND_LEAVE_PAYOUT)
        assert entry.account == AccountKind.GROSS_EARNINGS

    def test_leave_payout_amount(self) -> None:
        """termination_leave_payout amount matches residual leave payout."""
        entries = _post(_zero_fiscal(termination_residual_leave_payout_annual=_V))
        entry = next(e for e in entries if e.pay_item_kind == _KIND_LEAVE_PAYOUT)
        assert entry.amount == _V

    def test_no_leave_payout_when_zero(self) -> None:
        """No termination_leave_payout when residual leave payout is zero."""
        entries = _post(_zero_fiscal())
        kinds = [e.pay_item_kind for e in entries]
        assert _KIND_LEAVE_PAYOUT not in kinds

    def test_leave_payout_entry_id_format(self) -> None:
        """entry_id follows termination_leave_payout_{year}_{month:02d} pattern."""
        entries = _post(_zero_fiscal(termination_residual_leave_payout_annual=_V))
        entry = next(e for e in entries if e.pay_item_kind == _KIND_LEAVE_PAYOUT)
        expected = f"termination_leave_payout_{_DATE.year}_{_DATE.month:02d}"
        assert entry.entry_id == expected


class TestTfrLiquidation:
    """post_arrears_termination_tfr posts TFR liquidation to TFR_ACCRUAL."""

    def test_tfr_liquidation_entry_exists(self) -> None:
        """tfr_liquidation entry posted when termination_tfr_liquidation_annual != 0."""
        entries = _post(_zero_fiscal(termination_tfr_liquidation_annual=_V))
        kinds = [e.pay_item_kind for e in entries]
        assert _KIND_TFR_LIQ in kinds

    def test_tfr_liquidation_account(self) -> None:
        """tfr_liquidation is posted to TFR_ACCRUAL."""
        entries = _post(_zero_fiscal(termination_tfr_liquidation_annual=_V))
        entry = next(e for e in entries if e.pay_item_kind == _KIND_TFR_LIQ)
        assert entry.account == AccountKind.TFR_ACCRUAL

    def test_tfr_liquidation_amount(self) -> None:
        """tfr_liquidation amount matches termination_tfr_liquidation_annual."""
        entries = _post(_zero_fiscal(termination_tfr_liquidation_annual=_V))
        entry = next(e for e in entries if e.pay_item_kind == _KIND_TFR_LIQ)
        assert entry.amount == _V

    def test_no_tfr_liquidation_when_zero(self) -> None:
        """No tfr_liquidation when termination_tfr_liquidation_annual is zero."""
        entries = _post(_zero_fiscal())
        kinds = [e.pay_item_kind for e in entries]
        assert _KIND_TFR_LIQ not in kinds

    def test_tfr_liquidation_entry_id_format(self) -> None:
        """entry_id follows tfr_liquidation_{year}_{month:02d} pattern."""
        entries = _post(_zero_fiscal(termination_tfr_liquidation_annual=_V))
        entry = next(e for e in entries if e.pay_item_kind == _KIND_TFR_LIQ)
        assert entry.entry_id == f"tfr_liquidation_{_DATE.year}_{_DATE.month:02d}"


class TestTfrAccrual:
    """post_arrears_termination_tfr posts TFR accrual to TFR_ACCRUAL."""

    def test_tfr_accrual_entry_exists(self) -> None:
        """tfr_accrual entry posted when tfr_annual is non-zero."""
        entries = _post(_zero_fiscal(tfr_annual=_V))
        kinds = [e.pay_item_kind for e in entries]
        assert _KIND_TFR_ACCRUAL in kinds

    def test_tfr_accrual_account(self) -> None:
        """tfr_accrual is posted to TFR_ACCRUAL."""
        entries = _post(_zero_fiscal(tfr_annual=_V))
        entry = next(e for e in entries if e.pay_item_kind == _KIND_TFR_ACCRUAL)
        assert entry.account == AccountKind.TFR_ACCRUAL

    def test_tfr_accrual_amount(self) -> None:
        """tfr_accrual amount matches tfr_annual."""
        entries = _post(_zero_fiscal(tfr_annual=_V))
        entry = next(e for e in entries if e.pay_item_kind == _KIND_TFR_ACCRUAL)
        assert entry.amount == _V

    def test_no_tfr_accrual_when_zero(self) -> None:
        """No tfr_accrual when tfr_annual is zero."""
        entries = _post(_zero_fiscal())
        kinds = [e.pay_item_kind for e in entries]
        assert _KIND_TFR_ACCRUAL not in kinds

    def test_tfr_accrual_entry_id_format(self) -> None:
        """entry_id follows tfr_accrual_{year}_{month:02d} pattern."""
        entries = _post(_zero_fiscal(tfr_annual=_V))
        entry = next(e for e in entries if e.pay_item_kind == _KIND_TFR_ACCRUAL)
        assert entry.entry_id == f"tfr_accrual_{_DATE.year}_{_DATE.month:02d}"


class TestZeroAmountsSkipped:
    """post_arrears_termination_tfr produces no entries when all amounts are zero."""

    def test_all_zero_produces_empty_ledger(self) -> None:
        """All-zero FiscalPay produces no ledger entries."""
        entries = _post(_zero_fiscal())
        assert entries == ()


class TestCompetencePeriod:
    """All entries carry the correct competence period."""

    @pytest.mark.parametrize(
        "field",
        [
            "contract_renewal_arrears_annual",
            "termination_residual_leave_payout_annual",
            "termination_tfr_liquidation_annual",
            "tfr_annual",
        ],
    )
    def test_competence_period_matches_as_of(self, field: str) -> None:
        """Each entry's competence period matches the as_of date."""
        entries = _post(_zero_fiscal(**{field: _V}))
        assert len(entries) == 1
        assert entries[0].competence_period.year == _DATE.year
        assert entries[0].competence_period.month == _DATE.month


class TestEntryCount:
    """Number of entries reflects non-zero arrears/termination/TFR components."""

    def test_all_four_components_produce_four_entries(self) -> None:
        """All four components populated yields four ledger entries."""
        fiscal = _zero_fiscal(
            contract_renewal_arrears_annual=_V,
            termination_residual_leave_payout_annual=_V,
            termination_tfr_liquidation_annual=_V,
            tfr_annual=_V,
        )
        entries = _post(fiscal)
        assert len(entries) == 4

    @pytest.mark.parametrize(
        "field",
        [
            "contract_renewal_arrears_annual",
            "termination_residual_leave_payout_annual",
            "termination_tfr_liquidation_annual",
            "tfr_annual",
        ],
    )
    def test_single_component_yields_one_entry(self, field: str) -> None:
        """Each individual component produces exactly one entry."""
        entries = _post(_zero_fiscal(**{field: _V}))
        assert len(entries) == 1
