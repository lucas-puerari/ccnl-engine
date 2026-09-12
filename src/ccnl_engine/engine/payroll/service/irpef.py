"""IRPEF (personal income tax) calculation.

Implements Art. 11 TUIR brackets and the Art. 13 co. 1 TUIR work-income
deduction (piecewise-linear schedule as modified by D.Lgs. 216/2023 and
confirmed by L. 207/2024), the trattamento integrativo (Art. 1 D.L.
3/2020 as updated by L. 207/2024), the addizionale regionale e comunale
IRPEF (Art. 50 TUIR; Art. 1 D.Lgs. 360/1998), and the sterilizzazione
detrazioni for redditi > EUR 200k (Art. 1 c. 3-4 L. 199/2025).

Not in scope for this module (handled elsewhere in the engine):
detrazioni per carichi di famiglia (Art. 12 TUIR) — applied by the
orchestrator when ``PayrollScenario.family`` is set.
"""

from __future__ import annotations

from decimal import ROUND_FLOOR, Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.engine.surtax.domain.rules import SurtaxBracket
    from ccnl_engine.engine.tax.domain.rules import (
        SterilizzazioneDetrazioniRules,
        TrattamentoIntegrativoRules,
        YearRules,
    )

_ZERO = Decimal(0)

# ---------------------------------------------------------------------------
# Art. 13 co. 1 TUIR — work-income deduction statutory constants (2026).
# Source: Agenzia delle Entrate, circolare 4/E/2025, p. 6.
# ---------------------------------------------------------------------------
_DETR_FLAT = Decimal(1955)  # flat deduction for RC ≤ 15 000
_DETR_A = Decimal(1910)  # base coefficient for RC > 15 000
_DETR_B_COEFF = Decimal(1190)  # variable coefficient for 15 000<RC≤28 000
_DETR_B_SPAN = Decimal(13000)  # 28 000 - 15 000
_DETR_C_SPAN = Decimal(22000)  # 50 000 - 28 000
_DETR_LO = Decimal(15000)  # lower threshold
_DETR_MID = Decimal(28000)  # mid threshold
_DETR_HIGH = Decimal(50000)  # upper threshold (zero above)
_DETR_INCREMENT = Decimal(65)  # Art. 13 co. 1 lett. b-bis increment
_INCREMENT_LO = Decimal(25000)  # lower bound of increment range
_INCREMENT_HI = Decimal(35000)  # upper bound of increment range
_SEVENTY_FIVE = Decimal(75)  # TI corrective (L. 207/2024 co. 3)
_TEN_THOUSAND = Decimal(10000)


def irpef_gross(taxable_income: Decimal, rules: YearRules) -> Decimal:
    """Compute gross IRPEF on taxable_income using marginal brackets.

    Returns:
        The gross IRPEF amount, rounded to two decimal places.
    """
    if taxable_income <= _ZERO:
        return _ZERO
    tax = _ZERO
    prev_limit = _ZERO
    for bracket in rules.irpef_brackets:
        if bracket.up_to is not None:
            bracket_top = bracket.up_to
            if taxable_income <= prev_limit:
                break
            taxable_in_bracket = min(taxable_income, bracket_top) - prev_limit
            tax += taxable_in_bracket * bracket.rate
            prev_limit = bracket_top
        elif taxable_income > prev_limit:
            tax += (taxable_income - prev_limit) * bracket.rate
    return money(tax)


def _trunc4(ratio: Decimal) -> Decimal:
    """Truncate *ratio* to four decimal places per Art. 13 co. 6 TUIR.

    Italian law requires intermediate ratios to be floored (not rounded)
    to four decimal places before multiplication.

    Returns:
        The ratio truncated toward zero to four decimal places.
    """
    return (ratio * _TEN_THOUSAND).to_integral_value(
        rounding=ROUND_FLOOR
    ) / _TEN_THOUSAND


def work_income_deduction(gross_income: Decimal) -> Decimal:
    """Compute the Art. 13 co. 1 TUIR work-income deduction.

    Implements the statutory piecewise formula (circolare AdE 4/E/2025, p. 6)
    with ratios truncated to four decimal places per Art. 13 co. 6 TUIR:

    - RC <= 15 000: EUR 1 955 (flat).
    - 15 000 < RC <= 28 000: 1910 + 1190 * trunc4((28000-RC)/13000).
    - 28 000 < RC <= 50 000: 1910 * trunc4((50000-RC)/22000).
    - RC > 50 000: zero.

    An additional EUR 65 increment applies when 25 000 < RC ≤ 35 000,
    overlapping both middle and upper bands.

    Args:
        gross_income: Reddito complessivo di riferimento (taxable income,
            i.e. RAL minus employee INPS contributions).

    Returns:
        The applicable deduction, rounded to two decimal places.
    """
    if gross_income <= _ZERO:
        return _ZERO
    if gross_income <= _DETR_LO:
        return money(_DETR_FLAT)
    increment = (
        _DETR_INCREMENT if _INCREMENT_LO < gross_income <= _INCREMENT_HI else _ZERO
    )
    if gross_income <= _DETR_MID:
        ratio = _trunc4((_DETR_MID - gross_income) / _DETR_B_SPAN)
        return money(_DETR_A + _DETR_B_COEFF * ratio + increment)
    if gross_income <= _DETR_HIGH:
        ratio = _trunc4((_DETR_HIGH - gross_income) / _DETR_C_SPAN)
        return money(_DETR_A * ratio + increment)
    return _ZERO


def trattamento_integrativo(
    gross_annual: Decimal,
    irpef_gross: Decimal,
    work_deduction: Decimal,
    relevant_deductions: Decimal,
    rules: TrattamentoIntegrativoRules,
) -> Decimal:
    """Compute the trattamento integrativo bonus (Art. 1 D.L. 3/2020).

    Two income bands apply different eligibility rules:

    - RC ≤ ``rules.threshold_mid`` (15 000): the bonus (up to
      ``rules.max_amount``) is granted when IRPEF lorda exceeds the Art. 13
      work-income deduction reduced by EUR 75 (Art. 1 co. 3 L. 207/2024).
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

    Args:
        gross_annual: Reddito complessivo di riferimento (RAL proxy).
        irpef_gross: IRPEF lorda (Art. 11 TUIR) before any deductions.
        work_deduction: Art. 13 co. 1 work-income deduction.
        relevant_deductions: Sum of Art. 12 + Art. 13 + qualifying Art. 15
            deductions used to verify the requisito in the 15 000-28 000 band.
        rules: Threshold and cap parameters from the tax data file.

    Returns:
        The trattamento integrativo amount, rounded to two decimal places.
    """
    if gross_annual > rules.threshold_upper:
        return _ZERO
    if gross_annual <= rules.threshold_mid:
        # Requisito: IRPEF > (detrazione Art. 13 - EUR 75 corrective).
        threshold = money(max(_ZERO, work_deduction - _SEVENTY_FIVE))
        return money(rules.max_amount) if irpef_gross > threshold else _ZERO
    # 15 000 < RC <= 28 000: bonus = min(max_amount, relevant_deductions - IRPEF).
    if relevant_deductions <= irpef_gross:
        return _ZERO
    return money(min(rules.max_amount, relevant_deductions - irpef_gross))


def surtax_from_brackets(
    taxable_income: Decimal,
    brackets: list[SurtaxBracket],
    exemption_threshold: Decimal = _ZERO,
) -> Decimal:
    """Compute addizionale IRPEF (regionale or comunale) via marginal brackets.

    The bracket structure mirrors IRPEF (Art. 11 TUIR): each bracket's rate
    applies only to income within that slice.  Regions and municipalities that
    set a single flat rate are represented as a single bracket with
    ``up_to=None``.

    Args:
        taxable_income: IRPEF taxable base (gross annual minus employee INPS).
        brackets: Ascending list of
            :class:`~ccnl_engine.engine.surtax.domain.rules.SurtaxBracket`
            entries; the last entry must have ``up_to=None``.
        exemption_threshold: Full-exemption threshold: if
            ``taxable_income <= exemption_threshold`` the surtax is zero.
            Defaults to zero (no exemption).

    Returns:
        Annual surtax amount, rounded to two decimal places.
    """
    if taxable_income <= exemption_threshold or taxable_income <= _ZERO:
        return _ZERO
    tax = _ZERO
    prev_limit = _ZERO
    for bracket in brackets:
        if bracket.up_to is not None:
            bracket_top = bracket.up_to
            if taxable_income <= prev_limit:
                break
            taxable_in_bracket = min(taxable_income, bracket_top) - prev_limit
            tax += taxable_in_bracket * bracket.rate
            prev_limit = bracket_top
        elif taxable_income > prev_limit:
            tax += (taxable_income - prev_limit) * bracket.rate
    return money(tax)


def apply_sterilizzazione_detrazioni(
    art15_total: Decimal,
    gross_annual: Decimal,
    rules: SterilizzazioneDetrazioniRules | None,
) -> Decimal:
    """Reduce Art. 15 oneri deductions by the statutory amount for high earners.

    Per Art. 1 c. 3-4 L. 199/2025 (R14): when ``gross_annual`` exceeds
    ``rules.threshold`` (EUR 200 000), the Art. 15 TUIR oneri deductions
    (19% detraibili) are reduced by ``rules.reduction`` (EUR 440).  The
    reduction targets only Art. 15 deductions; Art. 12 (family) and Art. 13
    (work-income) deductions are not affected.

    Returns:
        Effective Art. 15 deduction, floored at zero.  When ``rules`` is
        ``None`` or income is at or below the threshold, ``art15_total`` is
        returned unchanged.
    """
    if rules is None or gross_annual <= rules.threshold:
        return art15_total
    return money(max(_ZERO, art15_total - rules.reduction))
