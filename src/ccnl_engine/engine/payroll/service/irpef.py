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
from ccnl_engine.engine.tax.domain.rules import WorkDeductionRules

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ccnl_engine.engine.surtax.domain.rules import SurtaxBracket
    from ccnl_engine.engine.tax.domain.rules import (
        SommaEsenteRules,
        SterilizzazioneDetrazioniRules,
        TrattamentoIntegrativoRules,
        UlterioreDetrazioneRules,
        YearRules,
    )

_ZERO = Decimal(0)
_ONE = Decimal(1)
_TEN_THOUSAND = Decimal(10000)
_DAYS_IN_YEAR = 365  # statutory denominator for Art. 13 co. 6 TUIR pro-rata

# Default Art. 13 constants (2026). Callers may pass rules.work_deduction instead.
_DEFAULT_WD = WorkDeductionRules()


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


def work_income_deduction(
    gross_income: Decimal,
    eligible_work_days: int = _DAYS_IN_YEAR,
    constants: WorkDeductionRules | None = None,
) -> Decimal:
    """Compute the Art. 13 co. 1 TUIR work-income deduction.

    Implements the statutory piecewise formula (circolare AdE 4/E/2025, p. 6)
    with ratios truncated to four decimal places per Art. 13 co. 6 TUIR:

    - RC <= 15 000: EUR 1 955 (flat).
    - 15 000 < RC <= 28 000: 1910 + 1190 * trunc4((28000-RC)/13000).
    - 28 000 < RC <= 50 000: 1910 * trunc4((50000-RC)/22000).
    - RC > 50 000: zero.

    An additional EUR 65 increment applies when 25 000 < RC ≤ 35 000,
    overlapping both middle and upper bands.

    The full-year amount is then scaled by
    ``trunc4(eligible_work_days / 365)`` per Art. 13 co. 6 TUIR.
    Pass ``eligible_work_days=365`` (the default) for a full year.

    Args:
        gross_income: Reddito complessivo di riferimento (taxable income,
            i.e. RAL minus employee INPS contributions).
        eligible_work_days: Calendar days in the tax year for which the
            worker is employed.  Determines the pro-rata ratio applied to
            the full-year deduction amount.
        constants: Versioned Art. 13 statutory constants. Defaults to the
            2026 schedule when ``None``.

    Returns:
        The applicable deduction, rounded to two decimal places.
    """
    c = constants if constants is not None else _DEFAULT_WD
    if gross_income <= _ZERO:
        return _ZERO
    if gross_income <= c.detr_lo:
        full_year = c.detr_flat
    else:
        increment = (
            c.detr_increment
            if c.increment_lo < gross_income <= c.increment_hi
            else _ZERO
        )
        if gross_income <= c.detr_mid:
            ratio = _trunc4((c.detr_mid - gross_income) / c.detr_b_span)
            full_year = c.detr_a + c.detr_b_coeff * ratio + increment
        elif gross_income <= c.detr_high:
            ratio = _trunc4((c.detr_high - gross_income) / c.detr_c_span)
            full_year = c.detr_a * ratio + increment
        else:
            return _ZERO
    if eligible_work_days == _DAYS_IN_YEAR:
        return money(full_year)
    prorata = _trunc4(Decimal(eligible_work_days) / _DAYS_IN_YEAR)
    return money(full_year * prorata)


def trattamento_integrativo(
    gross_annual: Decimal,
    irpef_gross: Decimal,
    work_deduction: Decimal,
    relevant_deductions: Decimal,
    rules: TrattamentoIntegrativoRules,
    eligible_work_days: int = _DAYS_IN_YEAR,
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

    Both ``rules.max_amount`` and the 75 EUR corrective are scaled by
    ``eligible_work_days / 365`` for part-year workers so that eligibility
    thresholds remain consistent when ``work_deduction`` is also pro-rated.

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
    c = constants if constants is not None else _DEFAULT_WD
    if gross_annual > rules.threshold_upper:
        return _ZERO
    if eligible_work_days == _DAYS_IN_YEAR:
        prorata = _ONE
        seventy_five = c.seventy_five
    else:
        prorata = _trunc4(Decimal(eligible_work_days) / _DAYS_IN_YEAR)
        seventy_five = money(c.seventy_five * prorata)
    max_amount = money(rules.max_amount * prorata)
    if gross_annual <= rules.threshold_mid:
        # Eligibility condition: IRPEF > (Art. 13 deduction - EUR 75 corrective).
        threshold = money(max(_ZERO, work_deduction - seventy_five))
        return max_amount if irpef_gross > threshold else _ZERO
    # 15 000 < RC <= 28 000: bonus = min(max_amount, relevant_deductions - IRPEF).
    if relevant_deductions <= irpef_gross:
        return _ZERO
    return money(min(max_amount, relevant_deductions - irpef_gross))


def ulteriore_detrazione_lavoro(
    taxable_income: Decimal,
    rules: UlterioreDetrazioneRules,
    eligible_work_days: int = _DAYS_IN_YEAR,
) -> Decimal:
    """Compute the ulteriore detrazione del lavoro dipendente (Art. 1 c. 6 L. 207/2024).

    Three income zones (reddito complessivo di riferimento):

    - ``rc <= threshold_low``: zero.
    - ``threshold_low < rc <= threshold_mid``: ``max_amount`` (flat).
    - ``threshold_mid < rc <= threshold_high``:
      ``max_amount * (threshold_high - rc) / (threshold_high - threshold_mid)``
      (linear taper to zero at ``threshold_high``).
    - ``rc > threshold_high``: zero.

    The full-year amount is scaled by ``eligible_work_days / 365``.
    Pass ``eligible_work_days=365`` (the default) for a full year.

    Args:
        taxable_income: Reddito complessivo di riferimento.
        rules: Threshold and amount parameters from the tax data file.
        eligible_work_days: Calendar days in the tax year for which the
            worker is employed.  Scales the result proportionally.

    Returns:
        The ulteriore detrazione amount (unrounded; pro-rated when
        ``eligible_work_days < 365``).
    """
    if taxable_income <= rules.threshold_low or taxable_income > rules.threshold_high:
        return _ZERO
    if taxable_income <= rules.threshold_mid:
        full_year = rules.max_amount
    else:
        span = rules.threshold_high - rules.threshold_mid
        full_year = rules.max_amount * (rules.threshold_high - taxable_income) / span
    if eligible_work_days == _DAYS_IN_YEAR:
        return full_year
    prorata = _trunc4(Decimal(eligible_work_days) / _DAYS_IN_YEAR)
    return full_year * prorata


def somma_esente(
    taxable_income: Decimal,
    rules: SommaEsenteRules,
) -> Decimal:
    """Compute the somma esente (L. 207/2024) for low-income workers.

    The bonus is added directly to net pay.  The applicable rate is the
    rate of the first band whose ``up_to`` value is >= ``taxable_income``;
    it is applied to the full ``taxable_income`` (not just the marginal
    slice).  Returns zero when ``taxable_income`` exceeds all band ceilings
    or is non-positive.

    Args:
        taxable_income: Reddito complessivo di riferimento.
        rules: Band schedule from the tax data file.

    Returns:
        The somma esente amount (unrounded; full-year).
    """
    if taxable_income <= _ZERO:
        return _ZERO
    for band in rules.bands:
        if taxable_income <= band.up_to:
            return taxable_income * band.rate
    return _ZERO


def surtax_from_brackets(
    taxable_income: Decimal,
    brackets: Sequence[SurtaxBracket],
    exemption_threshold: Decimal = _ZERO,
) -> Decimal:
    """Compute addizionale IRPEF (regionale or comunale) via marginal brackets.

    The bracket structure mirrors IRPEF (Art. 11 TUIR): each bracket's rate
    applies only to income within that slice.  Regions and municipalities that
    set a single flat rate are represented as a single bracket with
    ``up_to=None``.

    Args:
        taxable_income: IRPEF taxable base (gross annual minus employee INPS).
        brackets: Ordered sequence of
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
    detrazioni_total: Decimal,
    taxable_income: Decimal,
    rules: SterilizzazioneDetrazioniRules | None,
) -> Decimal:
    """Reduce oneri detraibili al 19% by the statutory amount for high earners.

    Per Art. 1 c. 3-4 L. 199/2025: when ``taxable_income`` (reddito
    complessivo) exceeds ``rules.threshold`` (EUR 200 000), the tax credit
    for oneri detraibili al 19% (Art. 15 c. 1 lett. a, b, d, e TUIR; not
    spese sanitarie lett. c) is reduced by ``rules.reduction`` (EUR 440),
    floored at zero.

    Returns:
        Effective deduction total, floored at zero.  When ``rules`` is
        ``None`` or income is at or below the threshold, ``detrazioni_total``
        is returned unchanged.
    """
    if rules is None or taxable_income <= rules.threshold:
        return detrazioni_total
    return money(max(_ZERO, detrazioni_total - rules.reduction))
