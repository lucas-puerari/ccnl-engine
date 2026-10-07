"""IRPEF credits of employment income with the reason for their amount.

The trattamento integrativo (Art. 1 D.L. 3/2020 as updated by L. 207/2024),
the ulteriore detrazione del lavoro dipendente (Art. 1 c. 6 L. 207/2024) and
the somma esente (Art. 1 c. 4-5 L. 207/2024).
Each ``*_outcome`` function returns the annual amount together with the
reason code of the rule branch that produced it, so the calculation decision
of the credit comes from the same branch as its amount.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.rounding import money
from ccnl_engine.payroll.service.irpef import DAYS_IN_YEAR
from ccnl_engine.payroll.service.irpef_deductions import (
    DEFAULT_WORK_DEDUCTION,
    for_days,
)

if TYPE_CHECKING:
    from ccnl_engine.tax.domain.credit_rules import (
        SommaEsenteRules,
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

    Two income bands apply different eligibility rules (c. 1):

    - RC <= ``rules.threshold_mid`` (15 000), first period: the bonus (up
      to ``rules.max_amount``) is granted when IRPEF lorda exceeds the
      Art. 13 c. 1 work-income deduction "diminuita dell'importo di 75 euro
      rapportato al periodo di lavoro nell'anno" (words inserted by
      L. 207/2024).

    - ``rules.threshold_mid`` < RC <= ``rules.threshold_upper`` (28 000),
      second and third periods: the bonus is due when the sum of the
      deductions of Art. 12 and Art. 13 c. 1 TUIR, and of the Art. 15 items
      listed there for loans and expenses up to 31 December 2021, exceeds
      IRPEF lorda; it equals that excess, capped at ``rules.max_amount``.
      The caller supplies the sum as ``relevant_deductions``.

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
        relevant_deductions: Sum of the deductions listed in c. 1, second
            period (Art. 12, Art. 13 c. 1 and the Art. 15 items known to the
            caller), compared with IRPEF lorda in the 15 000-28 000 band.
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
    c = constants if constants is not None else DEFAULT_WORK_DEDUCTION
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
    # 15 000 < RC <= 28 000 (c. 1, second and third periods):
    # bonus = min(max_amount, relevant_deductions - IRPEF).
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


def somma_esente(
    taxable_income: Decimal,
    rules: SommaEsenteRules,
    eligible_work_days: int = DAYS_IN_YEAR,
    external_income: Decimal = _ZERO,
) -> Decimal:
    """Compute the somma esente of L. 207/2024 art. 1 c. 4-5.

    - Eligibility (c. 4): reddito complessivo not above the last band's
      ``up_to`` (20,000 EUR).  The reddito complessivo is the employment
      income plus ``external_income``, which the caller states net of the
      main dwelling (c. 9: "al netto del reddito dell'unità immobiliare
      adibita ad abitazione principale e di quello delle relative
      pertinenze").
    - Percentage (c. 5): chosen on the employment income "rapportato
      all'intero anno", ``income * 365 / days`` (circolare AdE 4/E of 16
      May 2025, par. 1.2, esempio 1); the rate of the first band whose
      ``up_to`` covers it, the last band's rate above every ``up_to``.
    - Amount (c. 4): the percentage times the employment income actually
      earned in the year, not the annualised one.

    Args:
        taxable_income: Employment income of the year.
        rules: Band schedule from the tax data file.
        eligible_work_days: Days of employment in the tax year, at most 365.
        external_income: Reddito complessivo of the year beyond this
            employment, zero when there is none or it is not known.

    Returns:
        The somma esente amount (unrounded; full-year), zero when not due.
    """
    if taxable_income <= _ZERO:
        return _ZERO
    if taxable_income + external_income > rules.bands[-1].up_to:
        return _ZERO
    annualised = taxable_income * DAYS_IN_YEAR / eligible_work_days
    rate = next(
        (band.rate for band in rules.bands if annualised <= band.up_to),
        rules.bands[-1].rate,
    )
    return taxable_income * rate
