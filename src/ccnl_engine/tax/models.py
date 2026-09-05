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

    **Uniform-IVS invariant**: ``employer_ivs_rate`` is a single scalar that
    applies uniformly across all worker categories.  When a category-specific
    rate is active, the IVS component is still taken from ``employer_ivs_rate``
    and the category non-IVS residual is ``category_rate - employer_ivs_rate``.
    This invariant is enforced by ``_InpsEmployerTier._check_ivs_rate``, which
    requires every category rate to be ≥ ``ivs_rate`` so the residual is
    non-negative.  A sector where the IVS rate genuinely varies by category
    would need a ``ivs_rate_by_category`` field.
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

    ``employee_ivs_rate`` and ``employer_ivs_rate_*`` carry the IVS-only
    portions of the corresponding total rates.  For apprentice employees the
    full rate is IVS (NASpI is employer-only for apprentice contracts).  For
    employers the statutory IVS-only rate is 10 % for large firms and steps
    up from 1.5 % / 3 % for small firms; NASpI (1.31 %) and CIGS (0.30 %)
    are non-IVS and must not be capped.
    """

    model_config = ConfigDict(extra="forbid")

    employee_rate: Decimal
    employee_ivs_rate: Decimal
    employer_rate_months_0_11: Decimal
    employer_ivs_rate_months_0_11: Decimal
    employer_rate_months_12_23: Decimal
    employer_ivs_rate_months_12_23: Decimal
    employer_rate_after: Decimal
    employer_ivs_rate_after: Decimal

    @model_validator(mode="after")
    def _check_ivs_rates(self) -> Self:
        pairs: list[tuple[str, Decimal, str, Decimal]] = [
            (
                "employee_ivs_rate",
                self.employee_ivs_rate,
                "employee_rate",
                self.employee_rate,
            ),
            (
                "employer_ivs_rate_months_0_11",
                self.employer_ivs_rate_months_0_11,
                "employer_rate_months_0_11",
                self.employer_rate_months_0_11,
            ),
            (
                "employer_ivs_rate_months_12_23",
                self.employer_ivs_rate_months_12_23,
                "employer_rate_months_12_23",
                self.employer_rate_months_12_23,
            ),
            (
                "employer_ivs_rate_after",
                self.employer_ivs_rate_after,
                "employer_rate_after",
                self.employer_rate_after,
            ),
        ]
        for ivs_name, ivs_val, total_name, total_val in pairs:
            if ivs_val > total_val:
                msg = f"{ivs_name} {ivs_val} cannot exceed {total_name} {total_val}"
                raise ValueError(msg)
        return self

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

    def employer_ivs_rate_at(self, months_elapsed: int) -> Decimal:
        """Return the IVS-only employer rate in force at ``months_elapsed``.

        Returns:
            The IVS portion of the employer rate applicable at the given month.
        """
        if months_elapsed < _APPRENTICE_SMALL_FIRM_STEP_1:
            return self.employer_ivs_rate_months_0_11
        if months_elapsed < _APPRENTICE_SMALL_FIRM_STEP_2:
            return self.employer_ivs_rate_months_12_23
        return self.employer_ivs_rate_after


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
        for cat, cat_rate in self.rate_by_category.items():
            if cat_rate < self.ivs_rate:
                msg = (
                    f"rate_by_category[{cat!r}] = {cat_rate} is below "
                    f"ivs_rate {self.ivs_rate}; non-IVS portion would be negative"
                )
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


class DomesticInpsHoursBracket(BaseModel):
    """Flat-hour rates for domestic workers with > ``weekly_hours_threshold`` h/week.

    Applies regardless of the worker's actual hourly wage; overrides all
    ``DomesticInpsWageBracket`` entries when the hours condition is met.
    """

    model_config = ConfigDict(extra="forbid")

    employee_per_hour: Decimal
    employer_per_hour: Decimal
    employer_per_hour_fixed_term: Decimal


class DomesticInpsWageBracket(BaseModel):
    """One hourly-wage bracket in the domestic INPS flat-rate table.

    ``hourly_rate_up_to`` is inclusive; ``None`` on the last entry means
    unbounded (covers any wage above the preceding bracket's threshold).
    """

    model_config = ConfigDict(extra="forbid")

    hourly_rate_up_to: Decimal | None
    employee_per_hour: Decimal
    employer_per_hour: Decimal
    employer_per_hour_fixed_term: Decimal


class DomesticInpsRates(BaseModel):
    """Flat per-hour INPS contribution table for lavoro domestico.

    The selector is two-dimensional (INPS Circ. 9/2026, table 1):
    * ``weekly_hours > weekly_hours_threshold`` → use ``hours_bracket``,
      regardless of the worker's actual wage.
    * otherwise → walk ``wage_brackets`` in ascending ``hourly_rate_up_to``
      order and use the first bracket whose threshold is not exceeded.

    ``wage_brackets`` must end with one entry whose ``hourly_rate_up_to``
    is ``None`` (the open-ended top bracket).
    """

    model_config = ConfigDict(extra="forbid")

    weekly_hours_threshold: int
    hours_bracket: DomesticInpsHoursBracket
    wage_brackets: list[DomesticInpsWageBracket]

    def resolve(
        self,
        hourly_rate: Decimal,
        weekly_hours: Decimal,
        *,
        is_fixed_term: bool,
    ) -> tuple[Decimal, Decimal]:
        """Return ``(employee_per_hour, employer_per_hour)`` for the scenario.

        Returns:
            A tuple of (employee contribution per hour, employer contribution
            per hour) based on weekly_hours and hourly_rate.

        Raises:
            ValueError: If no wage bracket covers the given hourly_rate.
        """
        if weekly_hours > self.weekly_hours_threshold:
            b = self.hours_bracket
            er = (
                b.employer_per_hour_fixed_term if is_fixed_term else b.employer_per_hour
            )
            return b.employee_per_hour, er
        for bracket in self.wage_brackets:
            if (
                bracket.hourly_rate_up_to is None
                or hourly_rate <= bracket.hourly_rate_up_to
            ):
                er = (
                    bracket.employer_per_hour_fixed_term
                    if is_fixed_term
                    else bracket.employer_per_hour
                )
                return bracket.employee_per_hour, er
        msg = f"no wage bracket covers hourly_rate={hourly_rate!r}"
        raise ValueError(msg)


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
    employee_ivs_rate: Decimal
    employer_rate: Decimal
    employer_ivs_rate: Decimal
    small_firm_max_employees: int = Field(ge=0)
    small_firm_employer_rate_months_0_11: Decimal
    small_firm_employer_ivs_rate_months_0_11: Decimal
    small_firm_employer_rate_months_12_23: Decimal
    small_firm_employer_ivs_rate_months_12_23: Decimal

    @model_validator(mode="after")
    def _check_ivs_rates(self) -> Self:
        pairs: list[tuple[str, Decimal, str, Decimal]] = [
            (
                "employee_ivs_rate",
                self.employee_ivs_rate,
                "employee_rate",
                self.employee_rate,
            ),
            (
                "employer_ivs_rate",
                self.employer_ivs_rate,
                "employer_rate",
                self.employer_rate,
            ),
            (
                "small_firm_employer_ivs_rate_months_0_11",
                self.small_firm_employer_ivs_rate_months_0_11,
                "small_firm_employer_rate_months_0_11",
                self.small_firm_employer_rate_months_0_11,
            ),
            (
                "small_firm_employer_ivs_rate_months_12_23",
                self.small_firm_employer_ivs_rate_months_12_23,
                "small_firm_employer_rate_months_12_23",
                self.small_firm_employer_rate_months_12_23,
            ),
        ]
        for ivs_name, ivs_val, total_name, total_val in pairs:
            if ivs_val > total_val:
                msg = f"{ivs_name} {ivs_val} cannot exceed {total_name} {total_val}"
                raise ValueError(msg)
        return self


class TfrRules(BaseModel):
    """TFR (severance pay) accrual rules (Art. 2120 c.c.)."""

    model_config = ConfigDict(extra="forbid")

    accrual_divisor: Decimal


class TrattamentoIntegrativoRules(BaseModel):
    """Parameters for the trattamento integrativo (Art. 1 D.L. 3/2020).

    The bonus is computed on gross annual income (RAL) as follows:

    - RAL <= ``threshold_mid``: ``max_amount`` if IRPEF lorda > detrazioni lavoro,
      else 0.
    - ``threshold_mid`` < RAL <= ``threshold_upper``:
      max(0, ``max_amount`` * (``threshold_upper`` - RAL)
      / (``threshold_upper`` - ``threshold_mid``)).
    - RAL > ``threshold_upper``: 0.
    """

    model_config = ConfigDict(extra="forbid")

    threshold_mid: Decimal
    threshold_upper: Decimal
    max_amount: Decimal


class _YearRulesRaw(BaseModel):
    """Full deserialization model for a tax/data/<year>-<sector>.json file.

    Either ``inps`` + ``apprentice`` (standard percentage model) or
    ``domestic_contributions`` (flat per-hour domestic model) must be present.
    Both combinations are validated by ``_check_contribution_model``.
    """

    model_config = ConfigDict(extra="forbid")

    year: int
    sector: str  # validated against TaxSector at load time
    irpef_brackets: list[IrpefBracket]
    work_deduction_breakpoints: list[DeductionBreakpoint]
    fixed_term_additional_rate: Decimal
    inps: _InpsRawRates | None = None
    apprentice: _ApprenticeRawRates | None = None
    domestic_contributions: DomesticInpsRates | None = None
    tfr: TfrRules
    trattamento_integrativo: TrattamentoIntegrativoRules | None = None
    notes: list[str] = []

    @model_validator(mode="after")
    def _check_contribution_model(self) -> Self:
        has_standard = self.inps is not None and self.apprentice is not None
        has_domestic = self.domestic_contributions is not None
        if not has_standard and not has_domestic:
            msg = (
                "tax file must contain either 'inps' + 'apprentice' "
                "(standard model) or 'domestic_contributions' (domestic model)"
            )
            raise ValueError(msg)
        return self


class YearRules(BaseModel):
    """All statutory tax and contribution parameters for a single fiscal year.

    ``inps`` and ``apprentice`` are set for standard sectors; ``None`` for
    domestic sectors where ``domestic_contributions`` carries the flat-rate
    table instead.  Exactly one contribution model is present (enforced by
    the loader, which mirrors ``_YearRulesRaw._check_contribution_model``).
    """

    model_config = ConfigDict(extra="forbid")

    year: int
    irpef_brackets: list[IrpefBracket]
    work_deduction_breakpoints: list[DeductionBreakpoint]
    fixed_term_additional_rate: Decimal
    inps: InpsRates | None = None
    apprentice: ApprenticeRates | None = None
    domestic_contributions: DomesticInpsRates | None = None
    tfr: TfrRules
    trattamento_integrativo: TrattamentoIntegrativoRules | None = None
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
