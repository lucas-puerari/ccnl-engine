"""IRPEF (personal income tax) calculation.

Implements Art. 11 TUIR brackets and the Art. 13 co. 1 TUIR work-income
deduction (piecewise-linear schedule as modified by D.Lgs. 216/2023 and
confirmed by L. 199/2025, Art. 1 c. 2), the somma esente (L. 207/2024), the
addizionale regionale e comunale IRPEF (Art. 50 TUIR; Art. 1 D.Lgs.
360/1998), and the sterilizzazione detrazioni for redditi > EUR 200k (Art. 1
c. 3-4 L. 199/2025).

Not in scope for this module (handled elsewhere in the engine):
detrazioni per carichi di famiglia (Art. 12 TUIR), applied by the
orchestrator when ``PayrollScenario.family`` is set; the trattamento
integrativo and the ulteriore detrazione, in
:mod:`~ccnl_engine.payroll.service.irpef_credits`.
"""

from __future__ import annotations

from decimal import ROUND_FLOOR, Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.service.rounding import money
from ccnl_engine.tax.domain.irpef_rules import WorkDeductionRules

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ccnl_engine.tax.domain.credit_rules import SommaEsenteRules
    from ccnl_engine.tax.domain.irpef_rules import SterilizzazioneDetrazioniRules
    from ccnl_engine.tax.domain.ruleset import YearRules
    from ccnl_engine.tax.domain.surtax_rules import SurtaxBracket

_ZERO = Decimal(0)
_TEN_THOUSAND = Decimal(10000)
DAYS_IN_YEAR = 365  # "365 per l'intero anno": 730/2026 istruzioni, quadro C

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
    """Truncate an income ratio of art. 13 TUIR to four decimal places.

    Art. 13 c. 6 TUIR: "Se il risultato dei rapporti indicati nei commi 1,
    3, 4 e 5 è maggiore di zero, lo stesso si assume nelle prime quattro
    cifre decimali".  It covers the income ratios of those commi only, not
    the proportion to the days of work (see :func:`for_days`).

    Returns:
        The ratio truncated toward zero to four decimal places.
    """
    return (ratio * _TEN_THOUSAND).to_integral_value(
        rounding=ROUND_FLOOR
    ) / _TEN_THOUSAND


def for_days(full_year: Decimal, eligible_work_days: int) -> Decimal:
    """Proportion a full-year credit to the days of work in the year.

    Art. 13 c. 1 TUIR, L. 207/2024 art. 1 c. 6 and D.L. 3/2020 art. 1 give
    the amount "rapportata al periodo di lavoro nell'anno"; the 730/2026
    istruzioni count the days of work with "365 per l'intero anno" (quadro
    C, periodo di lavoro), so the amount is ``amount * days / 365``.  The
    four-decimal truncation of art. 13 c. 6 TUIR is not applied: the days
    are not one of the ratios it lists.  The full-year amount is rounded to
    cents first, as the tables state it in euro.

    Returns:
        ``money(money(full_year) * eligible_work_days / 365)``.
    """
    return money(money(full_year) * eligible_work_days / DAYS_IN_YEAR)


def work_income_deduction(
    gross_income: Decimal,
    eligible_work_days: int = DAYS_IN_YEAR,
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

    The full-year amount is then proportioned to the days by
    :func:`for_days`, without truncating ``eligible_work_days / 365``.
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
    return for_days(full_year, eligible_work_days)


def somma_esente(
    taxable_income: Decimal,
    rules: SommaEsenteRules,
    eligible_work_days: int = DAYS_IN_YEAR,
) -> Decimal:
    """Compute the somma esente of L. 207/2024 art. 1 c. 4-5.

    - Eligibility (c. 4): reddito complessivo not above the last band's
      ``up_to`` (20,000 EUR).  Employment income is the only income the
      engine knows, so it stands for the reddito complessivo.
    - Percentage (c. 5): chosen on the employment income "rapportato
      all'intero anno", ``income * 365 / days`` (circolare AdE 4/E of 16
      May 2025, par. 1.2, esempio 1); the rate of the first band whose
      ``up_to`` covers it, the last band's rate above every ``up_to``.
    - Amount (c. 4): the percentage times the employment income actually
      earned in the year, not the annualised one.

    Args:
        taxable_income: Employment income of the year, also used as the
            reddito complessivo.
        rules: Band schedule from the tax data file.
        eligible_work_days: Days of employment in the tax year, at most 365.

    Returns:
        The somma esente amount (unrounded; full-year), zero when not due.
    """
    if taxable_income <= _ZERO or taxable_income > rules.bands[-1].up_to:
        return _ZERO
    annualised = taxable_income * DAYS_IN_YEAR / eligible_work_days
    rate = next(
        (band.rate for band in rules.bands if annualised <= band.up_to),
        rules.bands[-1].rate,
    )
    return taxable_income * rate


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
            :class:`~ccnl_engine.tax.domain.surtax_rules.SurtaxBracket`
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
