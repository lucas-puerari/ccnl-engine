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

from decimal import Decimal
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


def work_income_deduction(gross_income: Decimal, rules: YearRules) -> Decimal:
    """Compute the Art. 13 TUIR work-income deduction via piecewise interpolation.

    Returns:
        The applicable deduction amount, rounded to two decimal places.
    """
    if gross_income <= _ZERO:
        return _ZERO
    points = rules.work_deduction_breakpoints
    first = points[0]
    if first.income_up_to is not None and gross_income <= first.income_up_to:
        return money(first.deduction)
    for i in range(len(points) - 1):
        lo = points[i]
        hi = points[i + 1]
        lo_income = lo.income_up_to
        hi_income = hi.income_up_to
        if lo_income is None:
            break  # pragma: no cover
        if hi_income is None:
            return money(hi.deduction)
        if lo_income < gross_income <= hi_income:
            return _interpolate_deduction(
                gross_income, lo_income, hi_income, lo.deduction, hi.deduction
            )
    return money(points[-1].deduction)


def trattamento_integrativo(
    gross_annual: Decimal,
    irpef_gross: Decimal,
    work_deduction: Decimal,
    rules: TrattamentoIntegrativoRules,
) -> Decimal:
    """Compute the trattamento integrativo bonus (Art. 1 D.L. 3/2020).

    Args:
        gross_annual: Annual gross pay (RAL) used to determine the bonus tier.
        irpef_gross: Gross IRPEF before work-income deduction (Art. 11 TUIR).
        work_deduction: Work-income deduction (Art. 13 TUIR).
        rules: Threshold and amount parameters from the tax data file.

    Returns:
        The trattamento integrativo amount, rounded to two decimal places.
        Zero when RAL exceeds ``rules.threshold_upper`` or when the bonus
        condition is not met.
    """
    if gross_annual > rules.threshold_upper:
        return _ZERO
    if gross_annual <= rules.threshold_mid:
        return money(rules.max_amount) if irpef_gross > work_deduction else _ZERO
    span = rules.threshold_upper - rules.threshold_mid
    scaled = rules.max_amount * (rules.threshold_upper - gross_annual) / span
    return money(max(_ZERO, scaled))


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
    work_deduction: Decimal,
    family_deduction: Decimal,
    gross_annual: Decimal,
    rules: SterilizzazioneDetrazioniRules | None,
) -> tuple[Decimal, Decimal]:
    """Reduce total detrazioni by the statutory amount for high earners.

    Per Art. 1 c. 3-4 L. 199/2025: when ``gross_annual`` exceeds
    ``rules.threshold`` (EUR 200 000), the total of Art. 13 work-income
    deduction and Art. 12 family deductions is reduced by
    ``rules.reduction`` (EUR 440 -- the exact clawback of the 35% to 33%
    bracket benefit on the EUR 28 000-50 000 slice).

    The reduction is absorbed first against ``work_deduction``, then
    against ``family_deduction``.  In practice, for income > EUR 50 000
    the work deduction is already 0, so the full reduction falls on the
    family deduction.

    Returns:
        A 2-tuple of (effective_work_deduction, effective_family_deduction),
        both floored at zero.  When ``rules`` is ``None`` or income is at or
        below the threshold, the inputs are returned unchanged.
    """
    if rules is None or gross_annual <= rules.threshold:
        return work_deduction, family_deduction
    total = work_deduction + family_deduction
    effective = money(max(_ZERO, total - rules.reduction))
    new_work = min(work_deduction, effective)
    new_family = effective - new_work
    return new_work, new_family


def _interpolate_deduction(
    gross_income: Decimal,
    lo_income: Decimal,
    hi_income: Decimal,
    lo_ded: Decimal,
    hi_ded: Decimal,
) -> Decimal:
    fraction = (gross_income - lo_income) / (hi_income - lo_income)
    return money(lo_ded + fraction * (hi_ded - lo_ded))
