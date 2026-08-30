"""Social security and TFR contribution calculations.

All functions return :class:`~decimal.Decimal` amounts rounded to the nearest
cent via :func:`~ccnl_engine.engine.rounding.money`.

.. note::
    **SIMPLIFICATION**: These functions apply a *uniform* rate over the entire
    gross annual pay. The IVS ceiling split (where contributions above a
    statutory ceiling accrue at a reduced rate) is not modelled because
    ``InpsRates.ceiling`` is ``None`` for the 2026 commerce sector data.
    When a ceiling is set, only the portion up to the ceiling is used as
    the contribution base (Art. 1 L. 335/1995).
"""

from decimal import Decimal

from ccnl_engine.engine.rounding import money
from ccnl_engine.tax.models import YearRules


def inps_employee(gross_annual: Decimal, rules: YearRules) -> Decimal:
    """Compute the employee-side INPS contribution.

    Args:
        gross_annual: Annual gross pay (imponibile previdenziale) in euros.
        rules: Tax year rules providing the employee contribution rate and
            optional ceiling.

    Returns:
        Employee INPS contribution, rounded to the nearest cent.
    """
    base = (
        min(gross_annual, rules.inps.ceiling)
        if rules.inps.ceiling is not None
        else gross_annual
    )
    return money(base * rules.inps.employee_rate)


def inps_employer(
    gross_annual: Decimal, rules: YearRules, *, fixed_term: bool = False
) -> Decimal:
    """Compute the employer-side INPS contribution.

    Includes the NASpI addizionale (Art. 2 co. 28 L. 92/2012) when
    *fixed_term* is ``True``.

    .. note::
        **SIMPLIFICATION**: The +0.50 % increment per fixed-term contract
        renewal is not modelled; only the base 1.4 % additional rate applies.

    Args:
        gross_annual: Annual gross pay in euros.
        rules: Tax year rules providing the employer contribution rate,
            ceiling, and fixed-term additional rate.
        fixed_term: Whether to add the NASpI addizionale on top of the
            standard employer rate.

    Returns:
        Employer INPS contribution (including NASpI addizionale when
        applicable), rounded to the nearest cent.
    """
    base = (
        min(gross_annual, rules.inps.ceiling)
        if rules.inps.ceiling is not None
        else gross_annual
    )
    rate = rules.inps.employer_rate
    if fixed_term:
        rate = rate + rules.fixed_term_additional_rate
    return money(base * rate)


def tfr(gross_annual: Decimal, rules: YearRules) -> Decimal:
    """Compute the annual TFR accrual.

    Uses the statutory divisor from Art. 2120 c.c. (``13.5`` by default).

    Args:
        gross_annual: Annual gross pay in euros.
        rules: Tax year rules providing the TFR accrual divisor.

    Returns:
        Annual TFR accrual, rounded to the nearest cent.
    """
    return money(gross_annual / rules.tfr.accrual_divisor)
