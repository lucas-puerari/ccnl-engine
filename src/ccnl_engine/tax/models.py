"""Tax rule models for a single fiscal year."""

from __future__ import annotations

from decimal import Decimal
from typing import Self

from pydantic import BaseModel, model_validator


class IrpefBracket(BaseModel):
    """A single IRPEF marginal tax bracket (Art. 11 TUIR)."""

    up_to: Decimal | None
    rate: Decimal


class DeductionBreakpoint(BaseModel):
    """A single breakpoint in the Art. 13 TUIR work-income deduction schedule."""

    income_up_to: Decimal | None
    deduction: Decimal


class InpsRates(BaseModel):
    """Resolved (flat) INPS contribution rates for a sector and employer size."""

    employee_rate: Decimal
    employer_rate: Decimal
    ceiling: Decimal | None


class _InpsEmployerTier(BaseModel):
    """A single employer-rate tier keyed by maximum headcount."""

    max_employees: int | None
    rate: Decimal


class _InpsRawRates(BaseModel):
    """Raw INPS block from the tax JSON file, before tier resolution."""

    employee_rate: Decimal
    employer_tiers: list[_InpsEmployerTier]
    ceiling: Decimal | None


class _YearRulesRaw(BaseModel):
    """Full deserialization model for a tax/data/<year>-<sector>.json file."""

    year: int
    sector: str  # validated against TaxSector at load time
    irpef_brackets: list[IrpefBracket]
    work_deduction_breakpoints: list[DeductionBreakpoint]
    fixed_term_additional_rate: Decimal
    inps: _InpsRawRates
    tfr: TfrRules
    notes: list[str] = []


class TfrRules(BaseModel):
    """TFR (severance pay) accrual rules (Art. 2120 c.c.)."""

    accrual_divisor: Decimal


class YearRules(BaseModel):
    """All statutory tax and contribution parameters for a single fiscal year."""

    year: int
    irpef_brackets: list[IrpefBracket]
    work_deduction_breakpoints: list[DeductionBreakpoint]
    fixed_term_additional_rate: Decimal
    inps: InpsRates
    tfr: TfrRules
    notes: list[str] = []

    @model_validator(mode="after")
    def _validate_sequences(self) -> Self:
        self._check_irpef_brackets()
        self._check_deduction_breakpoints()
        return self

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
