"""Tax rule models for a single fiscal year.

These models hold the Italian statutory rates and breakpoints needed to compute
IRPEF (personal income tax), INPS (social security) contributions, and TFR
(severance pay accrual). Values are loaded from
``tax/data/<year>-<sector>.json``; see :func:`ccnl_engine.data.load_year_rules`.

Public surface
--------------
- :class:`InpsRates` — resolved (flat) INPS contribution rates.
- :class:`YearRules` — all statutory parameters for a fiscal year, resolved for
  a specific sector and employer size.

Internal (prefixed ``_``)
--------------------------
- :class:`_InpsEmployerTier` — a single employer-rate tier keyed by headcount.
- :class:`_InpsRawRates` — raw INPS block from the JSON file (before tier
  resolution).
- :class:`_YearRulesRaw` — full deserialization model for a tax data file; used
  only by :func:`ccnl_engine.data.load_year_rules`.

All monetary values use :class:`decimal.Decimal`; rates are expressed as
fractions (e.g. ``Decimal("0.23")`` for 23 %).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Self

from pydantic import BaseModel, model_validator


class IrpefBracket(BaseModel):
    """A single IRPEF marginal tax bracket (Art. 11 TUIR).

    Attributes:
        up_to: Upper bound of the bracket in euros. ``None`` for the last
            (unbounded) bracket.
        rate: Marginal rate as a fraction, e.g. ``Decimal("0.23")`` for 23 %.
    """

    up_to: Decimal | None
    rate: Decimal


class DeductionBreakpoint(BaseModel):
    """A single breakpoint in the Art. 13 TUIR work-income deduction schedule.

    Breakpoints are stored in ascending order of ``income_up_to``. The engine
    performs piecewise-linear interpolation between consecutive breakpoints.
    For income below the first breakpoint's ``income_up_to``, the first
    breakpoint's ``deduction`` applies (flat segment). For income above the
    last finite breakpoint, the deduction is zero.

    Attributes:
        income_up_to: Upper bound (inclusive) of this segment in euros.
            ``None`` for the final open-ended entry.
        deduction: Deduction amount at the top of this segment (euros).
    """

    income_up_to: Decimal | None
    deduction: Decimal


class InpsRates(BaseModel):
    """Resolved (flat) INPS contribution rates for a sector and employer size.

    Produced by :func:`ccnl_engine.data.load_year_rules` after resolving the
    employer-tier table from the raw JSON file.  This is what :func:`compute`
    sees — a single scalar per rate, no tier logic.

    Attributes:
        employee_rate: Employee-side contribution rate (fraction).
        employer_rate: Employer-side contribution rate (fraction), including
            all employer charges (CUAF, etc.) but *excluding* the fixed-term
            additional contribution (NASpI addizionale), held separately in
            :attr:`YearRules.fixed_term_additional_rate`.
        ceiling: Annual contributory ceiling in euros. ``None`` if uncapped.
    """

    employee_rate: Decimal
    employer_rate: Decimal
    ceiling: Decimal | None


# ---------------------------------------------------------------------------
# Internal raw models — used only by ccnl_engine.data.load_year_rules
# ---------------------------------------------------------------------------


class _InpsEmployerTier(BaseModel):
    """A single employer-rate tier keyed by maximum headcount.

    Tiers must be stored in ascending order of ``max_employees`` in the JSON
    file, with exactly one entry having ``max_employees=None`` (open upper
    bound) as the last element.

    Attributes:
        max_employees: Upper bound (inclusive) on the number of employees for
            this tier. ``None`` means "no upper bound" (open tier).
        rate: Employer contribution rate (fraction) for this tier.
    """

    max_employees: int | None
    rate: Decimal


class _InpsRawRates(BaseModel):
    """Raw INPS block from the tax JSON file, before tier resolution.

    Attributes:
        employee_rate: Employee-side contribution rate (fraction). May also
            vary by size in some sectors; if so a future version will add
            ``employee_tiers`` following the same pattern.
        employer_tiers: Employer-rate tiers, sorted ascending by
            ``max_employees``, last entry open (``max_employees=None``).
        ceiling: Annual contributory ceiling in euros. ``None`` if uncapped.
    """

    employee_rate: Decimal
    employer_tiers: list[_InpsEmployerTier]
    ceiling: Decimal | None


class _YearRulesRaw(BaseModel):
    """Full deserialization model for a ``tax/data/<year>-<sector>.json`` file.

    This is an internal model used exclusively by
    :func:`ccnl_engine.data.load_year_rules` to parse the JSON and resolve
    tier-based rates into a flat :class:`YearRules`.  It is not exported from
    the package.

    Attributes:
        year: Four-digit fiscal year.
        sector: INPS sector this file covers, matches :class:`TaxSector`.
        irpef_brackets: Same structure as :attr:`YearRules.irpef_brackets`.
        work_deduction_breakpoints: Same as in :class:`YearRules`.
        fixed_term_additional_rate: NASpI addizionale base rate.
        inps: Raw INPS block with employer tiers.
        tfr: TFR accrual rules.
        notes: Free-text notes (assumptions, simplifications).
    """

    year: int
    sector: str  # validated against TaxSector at load time
    irpef_brackets: list[IrpefBracket]
    work_deduction_breakpoints: list[DeductionBreakpoint]
    fixed_term_additional_rate: Decimal
    inps: _InpsRawRates
    tfr: TfrRules
    notes: list[str] = []


class TfrRules(BaseModel):
    """TFR (severance pay) accrual rules.

    Attributes:
        accrual_divisor: Divisor applied to gross annual pay (Art. 2120 c.c.).
            Statutory value: ``Decimal("13.5")``.
    """

    accrual_divisor: Decimal


class YearRules(BaseModel):
    """All statutory tax and contribution parameters for a single fiscal year.

    Cross-field invariants enforced at construction:

    1. ``irpef_brackets`` must be non-empty; no intermediate bracket may have
       ``up_to=None``; ``up_to`` values must be strictly ascending; the last
       bracket must be unbounded (``up_to=None``).
    2. ``work_deduction_breakpoints`` must be non-empty; no intermediate entry
       may have ``income_up_to=None``; ``income_up_to`` values must be strictly
       ascending; the last entry must have ``income_up_to=None``.

    Attributes:
        year: Four-digit fiscal year (e.g. ``2026``).
        irpef_brackets: IRPEF marginal brackets, sorted ascending by
            ``up_to``, last entry unbounded.
        work_deduction_breakpoints: Art. 13 TUIR deduction schedule,
            sorted ascending, last entry has ``income_up_to=None``.
        fixed_term_additional_rate: NASpI addizionale rate for fixed-term
            contracts (employer-only, applied on top of
            ``inps.employer_rate``).
        inps: INPS contribution rates.
        tfr: TFR accrual rules.
        notes: Free-text notes (assumptions, simplifications, gaps).
    """

    year: int
    irpef_brackets: list[IrpefBracket]
    work_deduction_breakpoints: list[DeductionBreakpoint]
    fixed_term_additional_rate: Decimal
    inps: InpsRates
    tfr: TfrRules
    notes: list[str] = []

    @model_validator(mode="after")
    def _validate_sequences(self) -> Self:
        """Validate ordering invariants on brackets and breakpoints."""
        self._check_irpef_brackets()
        self._check_deduction_breakpoints()
        return self

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _check_irpef_brackets(self) -> None:
        brackets = self.irpef_brackets
        if not brackets:
            msg = "irpef_brackets must not be empty"
            raise ValueError(msg)
        for i, b in enumerate(brackets[:-1]):
            if b.up_to is None:
                msg = (
                    f"only the last irpef_bracket may have up_to=None "
                    f"(bracket {i} is not the last)"
                )
                raise ValueError(msg)
            next_b = brackets[i + 1]
            if next_b.up_to is not None and next_b.up_to <= b.up_to:
                msg = (
                    f"irpef_brackets must have strictly ascending up_to: "
                    f"bracket {i} up_to={b.up_to} >= "
                    f"bracket {i + 1} up_to={next_b.up_to}"
                )
                raise ValueError(msg)
        if brackets[-1].up_to is not None:
            msg = (
                "last irpef_bracket must be unbounded (up_to=None), "
                f"got up_to={brackets[-1].up_to}"
            )
            raise ValueError(msg)

    def _check_deduction_breakpoints(self) -> None:
        points = self.work_deduction_breakpoints
        if not points:
            msg = "work_deduction_breakpoints must not be empty"
            raise ValueError(msg)
        for i, p in enumerate(points[:-1]):
            if p.income_up_to is None:
                msg = (
                    f"only the last deduction breakpoint may have "
                    f"income_up_to=None (point {i} is not the last)"
                )
                raise ValueError(msg)
            next_p = points[i + 1]
            if next_p.income_up_to is not None and (
                next_p.income_up_to <= p.income_up_to
            ):
                msg = (
                    f"work_deduction_breakpoints must have strictly ascending "
                    f"income_up_to: point {i} income_up_to={p.income_up_to} >= "
                    f"point {i + 1} income_up_to={next_p.income_up_to}"
                )
                raise ValueError(msg)
        if points[-1].income_up_to is not None:
            msg = (
                "last deduction breakpoint must be unbounded (income_up_to=None), "
                f"got income_up_to={points[-1].income_up_to}"
            )
            raise ValueError(msg)
