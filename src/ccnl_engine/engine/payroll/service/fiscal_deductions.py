"""Deductions stage: trattamento integrativo, family, Art. 15."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.fiscal import FiscalSimplification
from ccnl_engine.engine.payroll.service import irpef as _irpef
from ccnl_engine.engine.payroll.service.art15_deductions import (
    compute_art15_deductions,
)
from ccnl_engine.engine.payroll.service.family_deductions import (
    compute_family_deductions,
)
from ccnl_engine.engine.payroll.service.rounding import money
from ccnl_engine.engine.tax.service.loaders import (
    load_art15_deduction_rules,
    load_family_deduction_rules,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.metadata import RulesetIdentity
    from ccnl_engine.engine.payroll.domain.scenario import PayrollScenario
    from ccnl_engine.engine.tax.domain.rules import YearRules

_ZERO = Decimal(0)


def _compute_ti(
    gross_annual: Decimal,
    irpef_gross: Decimal,
    work_income_deduction: Decimal,
    relevant_deductions: Decimal,
    rules: YearRules,
    eligible_work_days: int = 365,
) -> tuple[Decimal, frozenset[FiscalSimplification]]:
    """Return (trattamento_integrativo, fiscal_simplifications) for the scenario.

    Returns:
        Tuple of (ti_amount, fiscal_simplifications_frozenset).
    """
    ti_rules = rules.trattamento_integrativo
    if ti_rules is not None:
        trattamento_integrativo = _irpef.trattamento_integrativo(
            gross_annual,
            irpef_gross,
            work_income_deduction,
            relevant_deductions,
            ti_rules,
            eligible_work_days,
            constants=rules.work_deduction,
        )
        simplifications: frozenset[FiscalSimplification] = frozenset({
            FiscalSimplification.NO_ADDIZIONALE_REGIONALE,
            FiscalSimplification.NO_ADDIZIONALE_COMUNALE,
            FiscalSimplification.NO_DETRAZIONI_FAMILIARI,
            FiscalSimplification.NO_DETRAZIONI_ART15_MORTGAGE,
            FiscalSimplification.PARTIAL_DETRAZIONI_ART15,
            FiscalSimplification.NO_BILATERAL_FUNDS,
            FiscalSimplification.NO_ASSEGNO_UNICO,
        })
    else:
        trattamento_integrativo = _ZERO
        # Explicitly enumerate only the flags appropriate when TI is absent.
        # Do NOT include ADDIZIONALE_*_UNKNOWN here: those are mutually
        # exclusive with NO_ADDIZIONALE_* and are resolved by _compute_addizionali.
        simplifications = frozenset({
            FiscalSimplification.NO_ADDIZIONALE_REGIONALE,
            FiscalSimplification.NO_ADDIZIONALE_COMUNALE,
            FiscalSimplification.NO_TRATTAMENTO_INTEGRATIVO,
            FiscalSimplification.NO_DETRAZIONI_FAMILIARI,
            FiscalSimplification.NO_DETRAZIONI_ART15_MORTGAGE,
            FiscalSimplification.PARTIAL_DETRAZIONI_ART15,
            FiscalSimplification.NO_BILATERAL_FUNDS,
            FiscalSimplification.NO_ASSEGNO_UNICO,
        })
    return trattamento_integrativo, simplifications


def _run_wr_family_deductions(
    scenario: PayrollScenario,
    reddito_complessivo: Decimal,
    irpef_gross: Decimal,
    work_income_deduction: Decimal,
    year: int,
    *,
    employer_withholds_irpef: bool,
) -> tuple[Decimal, Decimal, Decimal, Decimal, Decimal, RulesetIdentity | None]:
    """Compute Art. 12 TUIR family deductions when ``scenario.family`` is set.

    Returns:
        A 6-tuple of (spouse_deduction, children_deduction, other_deduction,
        total_deduction, unused_deduction, ruleset_identity).
    """
    family = scenario.family
    if family is None or not family.has_any_dependent:
        return _ZERO, _ZERO, _ZERO, _ZERO, _ZERO, None
    rules = load_family_deduction_rules(year)
    spouse, children, other, total = compute_family_deductions(
        family, reddito_complessivo, rules
    )
    if not employer_withholds_irpef:
        return spouse, children, other, total, total, rules.ruleset
    available = money(max(_ZERO, irpef_gross - work_income_deduction))
    unused = money(max(_ZERO, total - available))
    return spouse, children, other, total, unused, rules.ruleset


def _run_wr_art15_deductions(
    scenario: PayrollScenario,
    irpef_gross: Decimal,
    work_income_deduction: Decimal,
    fam_total: Decimal,
    ulteriore_detrazione_lavoro: Decimal,
    year: int,
    *,
    employer_withholds_irpef: bool,
) -> tuple[Decimal, Decimal, RulesetIdentity | None]:
    """Compute Art. 15 TUIR deductions when ``scenario.art15_deductions`` is set.

    Returns:
        A 3-tuple of (art15_total, art15_unused, ruleset_identity).
    """
    art15 = scenario.art15_deductions
    if art15 is None or not art15.has_any_onere:
        return _ZERO, _ZERO, None
    rules = load_art15_deduction_rules(year)
    total = compute_art15_deductions(art15, rules)
    if not employer_withholds_irpef:
        return total, total, rules.ruleset
    available = money(
        max(
            _ZERO,
            irpef_gross
            - work_income_deduction
            - fam_total
            - ulteriore_detrazione_lavoro,
        )
    )
    unused = money(max(_ZERO, total - available))
    return total, unused, rules.ruleset
