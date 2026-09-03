"""Tax rule models for a single fiscal year."""

from __future__ import annotations

from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

_APPRENTICE_SMALL_FIRM_STEP_1 = 12
_APPRENTICE_SMALL_FIRM_STEP_2 = 24


class IrpefBracket(BaseModel):
    """A single IRPEF marginal tax bracket (Art. 11 TUIR)."""

    model_config = ConfigDict(extra="forbid")

    up_to: Decimal | None
    rate: Decimal


class DeductionBreakpoint(BaseModel):
    """A single breakpoint in the Art. 13 TUIR work-income deduction schedule."""

    model_config = ConfigDict(extra="forbid")

    income_up_to: Decimal | None
    deduction: Decimal


class InpsRates(BaseModel):
    """Resolved (flat) INPS contribution rates for a sector and employer size.

    ``employer_rate_by_category`` overrides ``employer_rate`` for levels whose
    ``category`` matches (e.g. lower rates for *impiegati* in artigianato).

    ``employee_ivs_rate`` and ``employer_ivs_rate`` are the IVS portions of
    the respective total rates.  When ``ceiling`` is set and
    ``ivs_ceiling_applies`` is passed to the contribution engine, only these
    portions are capped at the massimale retributivo; the remainder is always
    applied to the full base.
    """

    model_config = ConfigDict(extra="forbid")

    employee_rate: Decimal
    employee_ivs_rate: Decimal
    employer_rate: Decimal
    employer_ivs_rate: Decimal
    ceiling: Decimal | None
    employer_rate_by_category: dict[str, Decimal] = {}

    def employer_rate_for(self, category: str | None) -> Decimal:
        """Return the employer rate applicable to a worker category.

        Returns:
            The employer contribution rate for the given worker category.
        """
        if category is None:
            return self.employer_rate
        return self.employer_rate_by_category.get(category, self.employer_rate)


class ApprenticeRates(BaseModel):
    """Resolved contribution rates for apprentices (L. 296/2006 art. 1 c. 773).

    Employer rates are already resolved for the employer's headcount: firms
    with at most ``small_firm_max_employees`` pay the reduced rates in the
    first two years, all others pay ``employer_rate_after`` throughout.
    """

    model_config = ConfigDict(extra="forbid")

    employee_rate: Decimal
    employer_rate_months_0_11: Decimal
    employer_rate_months_12_23: Decimal
    employer_rate_after: Decimal

    def employer_rate_at(self, months_elapsed: int) -> Decimal:
        """Return the employer rate in force at ``months_elapsed``.

        Returns:
            The employer contribution rate applicable at the given month.
        """
        if months_elapsed < _APPRENTICE_SMALL_FIRM_STEP_1:
            return self.employer_rate_months_0_11
        if months_elapsed < _APPRENTICE_SMALL_FIRM_STEP_2:
            return self.employer_rate_months_12_23
        return self.employer_rate_after


class _InpsEmployerTier(BaseModel):
    """A single employer-rate tier keyed by maximum headcount.

    ``ivs_rate`` is the IVS (Invalidità, Vecchiaia, Superstiti) portion of
    ``rate``.  Only this portion is subject to the annual massimale retributivo
    (Art. 1 c. 18 L. 335/1995); the remainder (NASpI, CUAF, CIG, etc.) is
    always applied to the full contribution base.
    """

    model_config = ConfigDict(extra="forbid")

    max_employees: int | None
    rate: Decimal
    ivs_rate: Decimal
    rate_by_category: dict[str, Decimal] = {}

    @model_validator(mode="after")
    def _check_ivs_rate(self) -> Self:
        if self.ivs_rate > self.rate:
            msg = f"ivs_rate {self.ivs_rate} cannot exceed rate {self.rate}"
            raise ValueError(msg)
        return self


class _InpsEmployeeTier(BaseModel):
    """A single employee-rate tier keyed by maximum headcount.

    ``ivs_rate`` is the IVS portion of ``rate`` (subject to the massimale).
    For most private-sector employees this equals the full rate; the 0.30%
    CIGS employee share (added above certain headcount thresholds) is *not*
    IVS and must be excluded from ``ivs_rate``.
    """

    model_config = ConfigDict(extra="forbid")

    max_employees: int | None
    rate: Decimal
    ivs_rate: Decimal

    @model_validator(mode="after")
    def _check_ivs_rate(self) -> Self:
        if self.ivs_rate > self.rate:
            msg = f"ivs_rate {self.ivs_rate} cannot exceed rate {self.rate}"
            raise ValueError(msg)
        return self


class _InpsRawRates(BaseModel):
    """Raw INPS block from the tax JSON file, before tier resolution."""

    model_config = ConfigDict(extra="forbid")

    employee_tiers: list[_InpsEmployeeTier]
    employer_tiers: list[_InpsEmployerTier]
    ceiling: Decimal | None


class _ApprenticeRawRates(BaseModel):
    """Raw apprentice block from the tax JSON file, before headcount resolution."""

    model_config = ConfigDict(extra="forbid")

    employee_rate: Decimal
    employer_rate: Decimal
    small_firm_max_employees: int = Field(ge=0)
    small_firm_employer_rate_months_0_11: Decimal
    small_firm_employer_rate_months_12_23: Decimal


class TfrRules(BaseModel):
    """TFR (severance pay) accrual rules (Art. 2120 c.c.)."""

    model_config = ConfigDict(extra="forbid")

    accrual_divisor: Decimal


class _YearRulesRaw(BaseModel):
    """Full deserialization model for a tax/data/<year>-<sector>.json file."""

    model_config = ConfigDict(extra="forbid")

    year: int
    sector: str  # validated against TaxSector at load time
    irpef_brackets: list[IrpefBracket]
    work_deduction_breakpoints: list[DeductionBreakpoint]
    fixed_term_additional_rate: Decimal
    inps: _InpsRawRates
    apprentice: _ApprenticeRawRates
    tfr: TfrRules
    notes: list[str] = []


class YearRules(BaseModel):
    """All statutory tax and contribution parameters for a single fiscal year."""

    model_config = ConfigDict(extra="forbid")

    year: int
    irpef_brackets: list[IrpefBracket]
    work_deduction_breakpoints: list[DeductionBreakpoint]
    fixed_term_additional_rate: Decimal
    inps: InpsRates
    apprentice: ApprenticeRates
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
