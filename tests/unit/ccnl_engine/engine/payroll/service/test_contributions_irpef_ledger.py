"""Unit tests for ledger_builder.post_contributions_and_taxes."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.engine.payroll.domain.bundle import make_bundle
from ccnl_engine.engine.payroll.domain.ledger import AccountKind, Ledger, LedgerEntry
from ccnl_engine.engine.payroll.service.fiscal import FiscalPay
from ccnl_engine.engine.payroll.service.ledger_builder import (
    post_contributions_and_taxes,
)
from ccnl_engine.engine.payroll.service.orchestrator import estimate_annual
from tests.unit.ccnl_engine.engine.payroll.service.builders import (
    _DATE,
    _RULES,
    _build_ccnl,
    _req,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import CCNL
    from ccnl_engine.engine.payroll.domain.calculation import Calculation

_DEFAULT_CCNL = _build_ccnl()
_WITHHOLDING_EXEMPT_CCNL = _build_ccnl(**{"meta.withholding_exempt": True})

_KIND_INPS_EMP = "inps_employee_contribution"
_KIND_INPS_ER = "inps_employer_contribution"
_KIND_INAIL = "inail_employer_contribution"
_KIND_IRPEF = "irpef"


def _calc(
    ccnl: CCNL = _DEFAULT_CCNL,
    inail_rate: Decimal | None = None,
) -> Calculation:
    """Run estimate_annual and return the Calculation.

    Returns:
        The resulting :class:`Calculation`.
    """
    bundle = make_bundle(ccnl, _RULES, None)
    return estimate_annual(_req(inail_rate=inail_rate), bundle=bundle)


def _emp_entry(calc: Calculation) -> LedgerEntry:
    """Return the INPS employee entry from a Calculation.

    Returns:
        The matching :class:`~ccnl_engine.engine.payroll.domain.ledger.LedgerEntry`.
    """
    return next(e for e in calc.ledger_entries if e.pay_item_kind == _KIND_INPS_EMP)


def _er_entry(calc: Calculation) -> LedgerEntry:
    """Return the INPS employer entry from a Calculation.

    Returns:
        The matching :class:`~ccnl_engine.engine.payroll.domain.ledger.LedgerEntry`.
    """
    return next(e for e in calc.ledger_entries if e.pay_item_kind == _KIND_INPS_ER)


def _irpef_entry(calc: Calculation) -> LedgerEntry:
    """Return the IRPEF entry from a Calculation.

    Returns:
        The matching :class:`~ccnl_engine.engine.payroll.domain.ledger.LedgerEntry`.
    """
    return next(e for e in calc.ledger_entries if e.pay_item_kind == _KIND_IRPEF)


def _inail_entry(calc: Calculation) -> LedgerEntry:
    """Return the INAIL entry from a Calculation.

    Returns:
        The matching :class:`~ccnl_engine.engine.payroll.domain.ledger.LedgerEntry`.
    """
    return next(e for e in calc.ledger_entries if e.pay_item_kind == _KIND_INAIL)


class TestPostContributionsEmployee:
    """post_contributions_and_taxes posts INPS employee to EMPLOYEE_CONTRIBUTIONS."""

    def test_inps_employee_entry_exists(self) -> None:
        """An inps_employee_contribution entry is posted for a standard worker."""
        calc = _calc()
        kinds = [e.pay_item_kind for e in calc.ledger_entries]
        assert _KIND_INPS_EMP in kinds

    def test_inps_employee_account(self) -> None:
        """INPS employee is posted to EMPLOYEE_CONTRIBUTIONS."""
        entry = _emp_entry(_calc())
        assert entry.account == AccountKind.EMPLOYEE_CONTRIBUTIONS

    def test_inps_employee_amount_nonzero(self) -> None:
        """INPS employee amount is positive and non-zero."""
        entry = _emp_entry(_calc())
        assert entry.amount > Decimal(0)

    def test_inps_employee_competence_period(self) -> None:
        """Competence period matches the as_of date."""
        entry = _emp_entry(_calc())
        assert entry.competence_period.year == _DATE.year
        assert entry.competence_period.month == _DATE.month

    def test_inps_employee_entry_id_format(self) -> None:
        """entry_id follows the inps_employee_{year}_{month:02d} pattern."""
        entry = _emp_entry(_calc())
        expected = f"inps_employee_{_DATE.year}_{_DATE.month:02d}"
        assert entry.entry_id == expected


class TestPostContributionsEmployer:
    """post_contributions_and_taxes posts INPS employer to EMPLOYER_CONTRIBUTIONS."""

    def test_inps_employer_entry_exists(self) -> None:
        """An inps_employer_contribution entry is posted for a standard worker."""
        calc = _calc()
        kinds = [e.pay_item_kind for e in calc.ledger_entries]
        assert _KIND_INPS_ER in kinds

    def test_inps_employer_account(self) -> None:
        """INPS employer is posted to EMPLOYER_CONTRIBUTIONS."""
        entry = _er_entry(_calc())
        assert entry.account == AccountKind.EMPLOYER_CONTRIBUTIONS

    def test_inps_employer_amount_nonzero(self) -> None:
        """INPS employer amount is positive and non-zero."""
        entry = _er_entry(_calc())
        assert entry.amount > Decimal(0)

    def test_inps_employer_amount_exceeds_employee(self) -> None:
        """Employer INPS share exceeds employee share (typical ratio)."""
        calc = _calc()
        emp = _emp_entry(calc)
        er = _er_entry(calc)
        assert er.amount > emp.amount

    def test_inps_employer_entry_id_format(self) -> None:
        """entry_id follows the inps_employer_{year}_{month:02d} pattern."""
        entry = _er_entry(_calc())
        expected = f"inps_employer_{_DATE.year}_{_DATE.month:02d}"
        assert entry.entry_id == expected


class TestPostContributionsInail:
    """post_contributions_and_taxes posts INAIL when inail_rate is set."""

    def test_no_inail_entry_without_rate(self) -> None:
        """No inail_employer_contribution when inail_rate is not set."""
        calc = _calc()
        kinds = [e.pay_item_kind for e in calc.ledger_entries]
        assert _KIND_INAIL not in kinds

    def test_inail_entry_present_with_rate(self) -> None:
        """An inail_employer_contribution is posted when inail_rate is set."""
        calc = _calc(inail_rate=Decimal("0.005"))
        kinds = [e.pay_item_kind for e in calc.ledger_entries]
        assert _KIND_INAIL in kinds

    def test_inail_account(self) -> None:
        """INAIL is posted to EMPLOYER_CONTRIBUTIONS."""
        entry = _inail_entry(_calc(inail_rate=Decimal("0.005")))
        assert entry.account == AccountKind.EMPLOYER_CONTRIBUTIONS

    def test_inail_amount(self) -> None:
        """INAIL amount equals gross_annual * inail_rate."""
        entry = _inail_entry(_calc(inail_rate=Decimal("0.005")))
        assert entry.amount == Decimal("60.00")

    def test_inail_entry_id_format(self) -> None:
        """entry_id follows the inail_employer_{year}_{month:02d} pattern."""
        entry = _inail_entry(_calc(inail_rate=Decimal("0.005")))
        expected = f"inail_employer_{_DATE.year}_{_DATE.month:02d}"
        assert entry.entry_id == expected


class TestPostIrpef:
    """post_contributions_and_taxes posts net IRPEF to IRPEF account."""

    def test_irpef_entry_exists(self) -> None:
        """An irpef entry is posted when the employer withholds IRPEF."""
        calc = _calc()
        kinds = [e.pay_item_kind for e in calc.ledger_entries]
        assert _KIND_IRPEF in kinds

    def test_irpef_account(self) -> None:
        """IRPEF is posted to the IRPEF account."""
        entry = _irpef_entry(_calc())
        assert entry.account == AccountKind.IRPEF

    def test_irpef_amount_nonzero(self) -> None:
        """IRPEF amount is positive and non-zero for a taxable worker."""
        entry = _irpef_entry(_calc())
        assert entry.amount > Decimal(0)

    def test_irpef_entry_id_format(self) -> None:
        """entry_id follows the irpef_{year}_{month:02d} pattern."""
        entry = _irpef_entry(_calc())
        expected = f"irpef_{_DATE.year}_{_DATE.month:02d}"
        assert entry.entry_id == expected

    def test_no_irpef_entry_when_withholding_exempt(self) -> None:
        """No irpef entry when CCNL marks the employer as withholding-exempt."""
        calc = _calc(ccnl=_WITHHOLDING_EXEMPT_CCNL)
        kinds = [e.pay_item_kind for e in calc.ledger_entries]
        assert _KIND_IRPEF not in kinds

    def test_irpef_competence_period(self) -> None:
        """Competence period matches the as_of date."""
        entry = _irpef_entry(_calc())
        assert entry.competence_period.year == _DATE.year
        assert entry.competence_period.month == _DATE.month


class TestLedgerEntryCountWithContributions:
    """Total entry count reflects earnings + contributions + IRPEF."""

    @pytest.mark.parametrize(
        ("inail_rate", "expected_count"),
        [
            (None, 4),
            (Decimal("0.005"), 5),
        ],
    )
    def test_entry_count(self, inail_rate: Decimal | None, expected_count: int) -> None:
        """Count: base_salary + inps_employee + inps_employer + irpef [+ inail]."""
        calc = _calc(inail_rate=inail_rate)
        assert len(calc.ledger_entries) == expected_count

    def test_withholding_exempt_reduces_count(self) -> None:
        """Withholding-exempt CCNL produces one fewer entry (no IRPEF)."""
        normal = _calc()
        exempt = _calc(ccnl=_WITHHOLDING_EXEMPT_CCNL)
        assert len(normal.ledger_entries) - len(exempt.ledger_entries) == 1


_ZERO = Decimal(0)


class TestPostContributionsZeroAmounts:
    """post_contributions_and_taxes skips entries whose amount is zero."""

    def _zero_fiscal(self) -> FiscalPay:
        """Build a FiscalPay with all INPS and IRPEF amounts at zero.

        Returns:
            A :class:`FiscalPay` with contribution and tax fields zeroed.
        """
        return FiscalPay(
            consumed_ruleset_ids=(),
            consumed_verifications={},
            inps_employee_annual=_ZERO,
            inps_employer_annual=_ZERO,
            inps_employee_additional_annual=_ZERO,
            inail_employer_annual=_ZERO,
            inps_employer_exemption_annual=_ZERO,
            maternity_inps_indemnity_annual=_ZERO,
            workplace_injury_inail_indemnity_annual=_ZERO,
            termination_tfr_liquidation_annual=_ZERO,
            employer_funds_annual=_ZERO,
            tfr_annual=_ZERO,
            bilateral_employee_annual=_ZERO,
            bilateral_employer_annual=_ZERO,
            taxable_income=_ZERO,
            irpef_gross=_ZERO,
            work_income_deduction=_ZERO,
            fam_spouse=_ZERO,
            fam_children=_ZERO,
            fam_other=_ZERO,
            fam_total=_ZERO,
            fam_unused=_ZERO,
            art15_total=_ZERO,
            art15_unused=_ZERO,
            sterilizzazione_clawback=_ZERO,
            ulteriore_detrazione_lavoro=_ZERO,
            somma_esente=_ZERO,
            irpef_net=_ZERO,
            conguaglio_annual=_ZERO,
            termination_residual_leave_payout_annual=_ZERO,
            contract_renewal_arrears_annual=_ZERO,
            una_tantum_annual=_ZERO,
            personal_withholdings_annual=_ZERO,
            additional_irpef_base_annual=_ZERO,
            health_fund_employee_annual=_ZERO,
            health_fund_employer_annual=_ZERO,
            territorial_supplement_annual=_ZERO,
            company_supplement_annual=_ZERO,
            trattamento_integrativo=_ZERO,
            addizionale_regionale=_ZERO,
            addizionale_comunale=_ZERO,
            net_annual=_ZERO,
            net_monthly=_ZERO,
            employer_cost_annual=_ZERO,
            employer_withholds_irpef=False,
            fiscal_simplifications=frozenset(),
        )

    def test_zero_inps_employee_produces_no_entry(self) -> None:
        """When inps_employee_annual is zero, no employee contribution entry."""
        ledger = Ledger()
        post_contributions_and_taxes(self._zero_fiscal(), _DATE, ledger)
        kinds = [e.pay_item_kind for e in ledger]
        assert _KIND_INPS_EMP not in kinds

    def test_zero_inps_employer_produces_no_entry(self) -> None:
        """When inps_employer_annual is zero, no employer contribution entry."""
        ledger = Ledger()
        post_contributions_and_taxes(self._zero_fiscal(), _DATE, ledger)
        kinds = [e.pay_item_kind for e in ledger]
        assert _KIND_INPS_ER not in kinds

    def test_all_zero_produces_empty_ledger(self) -> None:
        """All-zero FiscalPay produces no ledger entries."""
        ledger = Ledger()
        post_contributions_and_taxes(self._zero_fiscal(), _DATE, ledger)
        assert ledger.entries() == ()
