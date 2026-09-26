"""Independent annual IRPEF oracle for employees, tax year 2026.

Written from the statutory text, deliberately without importing anything from
``ccnl_engine``.  It answers one question: given the final annual taxable
employment income, what is the net ordinary IRPEF owed for the year?

Scope (anything outside raises :class:`ValueError`):

- an employment of 1 to 365 days in the year; the art. 13 deduction and the
  further deduction are multiplied by ``days / 365`` ("rapportata al
  periodo di lavoro nell'anno") after the full-year amount is rounded to
  cents.  The day ratio is not truncated: the four-decimal rule quoted
  below is read as applying to the income ratios only;
- employment income is the only income (reddito complessivo equals the
  employment income, no deduzioni from the art. 10 TUIR base);
- no family deductions and no other art. 15 TUIR deductions;
- reddito complessivo not above 200,000 EUR (the reduction of deductions
  above that threshold is not modelled).

Credits paid on top of IRPEF (trattamento integrativo, somma esente
L. 207/2024 art. 1 c. 4) are separate cash items and are not part of the
figure returned here.

Sources (formulas transcribed on 26 September 2026; not yet cross-checked
against an official worked example):

- Brackets: art. 11 c. 1 TUIR as replaced by D.Lgs. 216/2023 art. 1 and
  amended by L. 199/2025 art. 1 c. 2 (second rate from 35% to 33%).
- Employment deduction: art. 13 c. 1 and c. 1.1 TUIR, as amended by
  D.Lgs. 216/2023 art. 1 c. 2 (1,955 EUR up to 15,000 EUR).
- Further deduction: L. 207/2024 art. 1 c. 6.
- Day pro-rata: art. 13 c. 1 TUIR and L. 207/2024 art. 1 c. 6, both
  "rapportata al periodo di lavoro nell'anno".
- Rounding of ratios: Agenzia delle Entrate, istruzioni modello 730 and
  Redditi PF, "il rapporto si assume nelle prime quattro cifre decimali".
"""

from __future__ import annotations

from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal

__all__ = [
    "employment_deduction",
    "further_deduction",
    "gross_irpef",
    "net_irpef",
]

_CENT = Decimal("0.01")
_RATIO_PLACES = Decimal("0.0001")
_ZERO = Decimal(0)
_MAX_SUPPORTED_INCOME = Decimal(200_000)
_DAYS_IN_YEAR = 365

# (upper bound of the bracket, marginal rate); ``None`` means no upper bound.
_BRACKETS_2026: tuple[tuple[Decimal | None, Decimal], ...] = (
    (Decimal(28_000), Decimal("0.23")),
    (Decimal(50_000), Decimal("0.33")),
    (None, Decimal("0.43")),
)


def _cents(amount: Decimal) -> Decimal:
    return amount.quantize(_CENT, rounding=ROUND_HALF_UP)


def _ratio(numerator: Decimal, denominator: Decimal) -> Decimal:
    """Return a statutory ratio truncated to four decimal places.

    Returns:
        ``numerator / denominator`` rounded down to 0.0001.
    """
    return (numerator / denominator).quantize(_RATIO_PLACES, rounding=ROUND_DOWN)


def _check_scope(income: Decimal) -> None:
    if income < _ZERO:
        msg = f"income must be >= 0; got {income}"
        raise ValueError(msg)
    if income > _MAX_SUPPORTED_INCOME:
        msg = f"income above {_MAX_SUPPORTED_INCOME} is outside the oracle scope"
        raise ValueError(msg)


def _check_days(days: int) -> None:
    if not 1 <= days <= _DAYS_IN_YEAR:
        msg = f"days must be 1-{_DAYS_IN_YEAR}; got {days}"
        raise ValueError(msg)


def _for_days(full_year: Decimal, days: int) -> Decimal:
    """Return a full-year deduction proportioned to ``days`` of employment.

    Returns:
        ``full_year * days / 365`` rounded to cents.
    """
    _check_days(days)
    return _cents(full_year * days / _DAYS_IN_YEAR)


def gross_irpef(income: Decimal) -> Decimal:
    """Return the imposta lorda on ``income`` using the 2026 brackets.

    Each slice of income between two bracket bounds is taxed at that
    bracket's marginal rate; the slices are summed and rounded to cents.

    Returns:
        Gross IRPEF in EUR, rounded to cents.
    """
    _check_scope(income)
    tax = _ZERO
    lower = _ZERO
    for upper, rate in _BRACKETS_2026:
        top = income if upper is None else min(income, upper)
        if top > lower:
            tax += (top - lower) * rate
        if upper is None or income <= upper:
            break
        lower = upper
    return _cents(tax)


def employment_deduction(income: Decimal, days: int = _DAYS_IN_YEAR) -> Decimal:
    """Return the art. 13 TUIR deduction for ``days`` of employment.

    - income <= 15,000: 1,955;
    - 15,000 < income <= 28,000: 1,910 + 1,190 * (28,000 - income) / 13,000;
    - 28,000 < income <= 50,000: 1,910 * (50,000 - income) / 22,000;
    - above 50,000: 0;
    - plus 65 when 25,000 < income <= 35,000 (art. 13 c. 1.1);
    - the full-year amount, rounded to cents, times ``days / 365``.

    Returns:
        Deduction in EUR, rounded to cents.
    """
    _check_scope(income)
    if income <= Decimal(15_000):
        base = Decimal(1_955)
    elif income <= Decimal(28_000):
        ratio = _ratio(Decimal(28_000) - income, Decimal(13_000))
        base = Decimal(1_910) + Decimal(1_190) * ratio
    elif income <= Decimal(50_000):
        ratio = _ratio(Decimal(50_000) - income, Decimal(22_000))
        base = Decimal(1_910) * ratio
    else:
        base = _ZERO
    bonus = Decimal(65) if Decimal(25_000) < income <= Decimal(35_000) else _ZERO
    return _for_days(_cents(base + bonus), days)


def further_deduction(income: Decimal, days: int = _DAYS_IN_YEAR) -> Decimal:
    """Return the L. 207/2024 art. 1 c. 6 further deduction.

    - 20,000 < income <= 32,000: 1,000;
    - 32,000 < income <= 40,000: 1,000 * (40,000 - income) / 8,000;
    - otherwise: 0 (below 20,000 the somma esente of c. 4 applies instead);
    - the full-year amount, rounded to cents, times ``days / 365``.

    Returns:
        Deduction in EUR, rounded to cents.
    """
    _check_scope(income)
    if Decimal(20_000) < income <= Decimal(32_000):
        full_year = Decimal("1000.00")
    elif Decimal(32_000) < income <= Decimal(40_000):
        ratio = _ratio(Decimal(40_000) - income, Decimal(8_000))
        full_year = _cents(Decimal(1_000) * ratio)
    else:
        full_year = Decimal("0.00")
    return _for_days(full_year, days)


def net_irpef(income: Decimal, days: int = _DAYS_IN_YEAR) -> Decimal:
    """Return the net annual ordinary IRPEF owed on ``income``.

    Net IRPEF is the gross tax minus the deductions, floored at zero because
    the deductions are not refundable (art. 13 and L. 207/2024 c. 6).

    Returns:
        Net IRPEF in EUR, rounded to cents.
    """
    deductions = employment_deduction(income, days) + further_deduction(income, days)
    return max(gross_irpef(income) - deductions, Decimal("0.00"))
