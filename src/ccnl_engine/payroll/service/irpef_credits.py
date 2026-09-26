"""IRPEF credits of employment income with the reason for their amount.

The trattamento integrativo (Art. 1 D.L. 3/2020 as updated by L. 207/2024)
and the ulteriore detrazione del lavoro dipendente (Art. 1 c. 6 L. 207/2024).
Each ``*_outcome`` function returns the annual amount together with the
reason code of the rule branch that produced it, so the calculation decision
of the credit comes from the same branch as its amount.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.rounding import money
from ccnl_engine.payroll.service.irpef import _DEFAULT_WD, DAYS_IN_YEAR, for_days

if TYPE_CHECKING:
    from ccnl_engine.tax.domain.credit_rules import (
        TrattamentoIntegrativoRules,
        UlterioreDetrazioneRules,
    )
    from ccnl_engine.tax.domain.irpef_rules import WorkDeductionRules

_ZERO = Decimal(0)


@dataclass(frozen=True, slots=True)
class CreditOutcome:
    """Annual amount of a tax credit and the rule branch that produced it.

    Attributes:
        amount: Annual amount, zero when the credit is not due.
        reason_code: Lower snake case code of the branch taken, e.g.
            ``"income_above_upper_threshold"``.
    """

    amount: Decimal
    reason_code: str


def trattamento_integrativo(
    gross_annual: Decimal,
    irpef_gross: Decimal,
    work_deduction: Decimal,
    relevant_deductions: Decimal,
    rules: TrattamentoIntegrativoRules,
    eligible_work_days: int = DAYS_IN_YEAR,
    constants: WorkDeductionRules | None = None,
) -> Decimal:
    """Compute the trattamento integrativo bonus (Art. 1 D.L. 3/2020).

    Two income bands apply different eligibility rules:

    - RC ≤ ``rules.threshold_mid`` (15 000): the bonus (up to
      ``rules.max_amount``) is granted when IRPEF lorda exceeds the Art. 13
      work-income deduction reduced by the EUR 75 corrective
      (Art. 1 co. 3 L. 207/2024, also pro-rated when part-year).
      The EUR 75 corrective offsets the 2025 deduction increase so that
      beneficiaries remain entitled.

    - ``rules.threshold_mid`` < RC ≤ ``rules.threshold_upper`` (28 000):
      the bonus equals the excess of relevant deductions over IRPEF lorda,
      capped at ``rules.max_amount``.  Relevant deductions are the sum of
      Art. 13 (work-income), Art. 12 (family), and qualifying Art. 15
      deductions (mortgages pre-2022 and specific other oneri).  When IRPEF
      lorda exceeds relevant deductions the requisito is not met and the
      bonus is zero.

    - RC > ``rules.threshold_upper``: zero.

    Both ``rules.max_amount`` and the 75 EUR corrective are proportioned to
    ``eligible_work_days / 365`` (not truncated) for part-year workers so
    that eligibility thresholds remain consistent when ``work_deduction``
    is also pro-rated.

    Args:
        gross_annual: Reddito complessivo di riferimento (taxable income).
        irpef_gross: IRPEF lorda (Art. 11 TUIR) before any deductions.
        work_deduction: Art. 13 co. 1 work-income deduction (already
            pro-rated when ``eligible_work_days < 365``).
        relevant_deductions: Sum of Art. 12 + Art. 13 + qualifying Art. 15
            deductions used to verify the requisito in the 15 000-28 000 band.
        rules: Threshold and cap parameters from the tax data file.
        eligible_work_days: Calendar days in the tax year for which the
            worker is employed.  Scales the max bonus and the 75 EUR
            corrective proportionally.
        constants: Versioned Art. 13 statutory constants (supplies the 75 EUR
            corrective). Defaults to the 2026 schedule when ``None``.

    Returns:
        The trattamento integrativo amount, rounded to two decimal places.
    """
    return trattamento_integrativo_outcome(
        gross_annual,
        irpef_gross,
        work_deduction,
        relevant_deductions,
        rules,
        eligible_work_days,
        constants,
    ).amount


def trattamento_integrativo_outcome(
    gross_annual: Decimal,
    irpef_gross: Decimal,
    work_deduction: Decimal,
    relevant_deductions: Decimal,
    rules: TrattamentoIntegrativoRules,
    eligible_work_days: int = DAYS_IN_YEAR,
    constants: WorkDeductionRules | None = None,
) -> CreditOutcome:
    """Compute the trattamento integrativo and the reason for its amount.

    Same rules and arguments as :func:`trattamento_integrativo`.

    Returns:
        The annual amount with reason ``income_above_upper_threshold``,
        ``full_amount`` or ``irpef_not_above_work_deduction`` (income up to
        ``threshold_mid``), ``deductions_above_irpef`` or
        ``deductions_not_above_irpef`` (income up to ``threshold_upper``).
    """
    c = constants if constants is not None else _DEFAULT_WD
    if gross_annual > rules.threshold_upper:
        return CreditOutcome(_ZERO, "income_above_upper_threshold")
    seventy_five = for_days(c.seventy_five, eligible_work_days)
    max_amount = for_days(rules.max_amount, eligible_work_days)
    if gross_annual <= rules.threshold_mid:
        # Eligibility condition: IRPEF > (Art. 13 deduction - EUR 75 corrective).
        threshold = money(max(_ZERO, work_deduction - seventy_five))
        if irpef_gross > threshold:
            return CreditOutcome(max_amount, "full_amount")
        return CreditOutcome(_ZERO, "irpef_not_above_work_deduction")
    # 15 000 < RC <= 28 000: bonus = min(max_amount, relevant_deductions - IRPEF).
    if relevant_deductions <= irpef_gross:
        return CreditOutcome(_ZERO, "deductions_not_above_irpef")
    amount = money(min(max_amount, relevant_deductions - irpef_gross))
    return CreditOutcome(amount, "deductions_above_irpef")


def ulteriore_detrazione_lavoro(
    taxable_income: Decimal,
    rules: UlterioreDetrazioneRules,
    eligible_work_days: int = DAYS_IN_YEAR,
) -> Decimal:
    """Compute the ulteriore detrazione del lavoro dipendente (Art. 1 c. 6 L. 207/2024).

    Three income zones (reddito complessivo di riferimento):

    - ``rc <= threshold_low``: zero.
    - ``threshold_low < rc <= threshold_mid``: ``max_amount`` (flat).
    - ``threshold_mid < rc <= threshold_high``:
      ``max_amount * (threshold_high - rc) / (threshold_high - threshold_mid)``
      (linear taper to zero at ``threshold_high``).  The ratio is not
      truncated: c. 6 does not refer to art. 13 c. 6 TUIR, whose
      four-decimal rule covers the ratios of art. 13 only.
    - ``rc > threshold_high``: zero.

    The full-year amount, rounded to cents, is proportioned to
    ``eligible_work_days / 365`` by :func:`~ccnl_engine.payroll.service\
.irpef.for_days`.
    Pass ``eligible_work_days=365`` (the default) for a full year.

    Args:
        taxable_income: Reddito complessivo di riferimento.
        rules: Threshold and amount parameters from the tax data file.
        eligible_work_days: Calendar days in the tax year for which the
            worker is employed.  Scales the result proportionally.

    Returns:
        The ulteriore detrazione amount, rounded to cents and pro-rated
        when ``eligible_work_days < 365``.
    """
    return ulteriore_detrazione_outcome(
        taxable_income, rules, eligible_work_days
    ).amount


def ulteriore_detrazione_outcome(
    taxable_income: Decimal,
    rules: UlterioreDetrazioneRules,
    eligible_work_days: int = DAYS_IN_YEAR,
) -> CreditOutcome:
    """Compute the ulteriore detrazione and the reason for its amount.

    Same rules and arguments as :func:`ulteriore_detrazione_lavoro`.

    Returns:
        The annual amount with reason ``income_not_above_lower_threshold``,
        ``income_above_upper_threshold``, ``full_amount`` or
        ``tapered_amount``.
    """
    if taxable_income <= rules.threshold_low:
        return CreditOutcome(_ZERO, "income_not_above_lower_threshold")
    if taxable_income > rules.threshold_high:
        return CreditOutcome(_ZERO, "income_above_upper_threshold")
    if taxable_income <= rules.threshold_mid:
        full_year, reason = rules.max_amount, "full_amount"
    else:
        span = rules.threshold_high - rules.threshold_mid
        full_year = rules.max_amount * (rules.threshold_high - taxable_income) / span
        reason = "tapered_amount"
    return CreditOutcome(for_days(full_year, eligible_work_days), reason)
