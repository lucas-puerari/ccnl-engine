"""INPS and social contribution rule models."""

from __future__ import annotations

from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.engine.contract.domain.category import WorkerCategory
from ccnl_engine.engine.primitives import (
    NonNegativeRate,
    PositiveCeiling,
    assert_ivs_le_total,
)
from ccnl_engine.engine.provenance.domain.chain import RuleProvenance


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
    This invariant is enforced by ``InpsEmployerTier._check_ivs_rate``, which
    requires every category rate to be >= ``ivs_rate`` so the residual is
    non-negative.  A sector where the IVS rate genuinely varies by category
    would need a ``ivs_rate_by_category`` field.

    ``employee_additional_rate`` and ``employee_additional_threshold`` model
    the 1% IVS contribution charged to employees on the portion of annual
    earnings exceeding the first pensionable band (Art. 3-ter D.L. 384/1992).
    When set, the additional is applied on top of the ordinary rate; it is
    IVS and therefore subject to the massimale when ``ivs_ceiling_applies``
    is True.  Both fields must be present together or both absent; the pair
    constraint is enforced by ``_check_rates``.  ``employee_additional_threshold``
    must be non-negative: a negative value would widen the contribution base
    beyond the actual pensionable earnings.
    """

    model_config = ConfigDict(extra="forbid")

    employee_rate: NonNegativeRate
    employee_ivs_rate: NonNegativeRate
    employer_rate: NonNegativeRate
    employer_ivs_rate: NonNegativeRate
    ceiling: PositiveCeiling | None
    employer_rate_by_category: dict[WorkerCategory, NonNegativeRate] = {}
    employee_additional_rate: NonNegativeRate | None = None
    employee_additional_threshold: NonNegativeRate | None = None
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _check_rates(self) -> Self:
        """Enforce IVS <= total invariants and paired additional fields.

        Returns:
            The validated instance.

        Raises:
            ValueError: If any IVS rate exceeds its total, or if only one of
                employee_additional_rate / employee_additional_threshold is
                set.
        """
        assert_ivs_le_total(
            "employee_ivs_rate",
            self.employee_ivs_rate,
            "employee_rate",
            self.employee_rate,
        )
        assert_ivs_le_total(
            "employer_ivs_rate",
            self.employer_ivs_rate,
            "employer_rate",
            self.employer_rate,
        )
        has_rate = self.employee_additional_rate is not None
        has_threshold = self.employee_additional_threshold is not None
        if has_rate != has_threshold:
            msg = (
                "employee_additional_rate and employee_additional_threshold "
                "must both be set or both be absent"
            )
            raise ValueError(msg)
        return self


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

    employee_rate: NonNegativeRate
    employee_ivs_rate: NonNegativeRate
    employer_rate_months_0_11: NonNegativeRate
    employer_ivs_rate_months_0_11: NonNegativeRate
    employer_rate_months_12_23: NonNegativeRate
    employer_ivs_rate_months_12_23: NonNegativeRate
    employer_rate_after: NonNegativeRate
    employer_ivs_rate_after: NonNegativeRate
    provenance: RuleProvenance | None = None

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
            assert_ivs_le_total(ivs_name, ivs_val, total_name, total_val)
        return self


class InpsEmployerTier(BaseModel):
    """A single employer-rate tier keyed by maximum headcount.

    ``ivs_rate`` is the IVS (Invalidità, Vecchiaia, Superstiti) portion of
    ``rate``.  Only this portion is subject to the annual massimale retributivo
    (Art. 1 c. 18 L. 335/1995); the remainder (NASpI, CUAF, CIG, etc.) is
    always applied to the full contribution base.
    """

    model_config = ConfigDict(extra="forbid")

    max_employees: int | None
    rate: NonNegativeRate
    ivs_rate: NonNegativeRate
    rate_by_category: dict[WorkerCategory, NonNegativeRate] = {}
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _check_ivs_rate(self) -> Self:
        assert_ivs_le_total("ivs_rate", self.ivs_rate, "rate", self.rate)
        for cat, cat_rate in self.rate_by_category.items():
            if cat_rate < self.ivs_rate:
                msg = (
                    f"rate_by_category[{cat.value!r}] = {cat_rate} is below "
                    f"ivs_rate {self.ivs_rate}; non-IVS portion would be negative"
                )
                raise ValueError(msg)
        return self


class InpsEmployeeTier(BaseModel):
    """A single employee-rate tier keyed by maximum headcount.

    ``ivs_rate`` is the IVS portion of ``rate`` (subject to the massimale).
    For most private-sector employees this equals the full rate; the 0.30%
    CIGS employee share (added above certain headcount thresholds) is *not*
    IVS and must be excluded from ``ivs_rate``.
    """

    model_config = ConfigDict(extra="forbid")

    max_employees: int | None
    rate: NonNegativeRate
    ivs_rate: NonNegativeRate
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _check_ivs_rate(self) -> Self:
        assert_ivs_le_total("ivs_rate", self.ivs_rate, "rate", self.rate)
        return self


class DomesticInpsHoursBracket(BaseModel):
    """Flat-hour rates for domestic workers with > ``weekly_hours_threshold`` h/week.

    Applies regardless of the worker's actual hourly wage; overrides all
    ``DomesticInpsWageBracket`` entries when the hours condition is met.
    """

    model_config = ConfigDict(extra="forbid")

    employee_per_hour: NonNegativeRate
    employer_per_hour: NonNegativeRate
    employer_per_hour_fixed_term: NonNegativeRate


class DomesticInpsWageBracket(BaseModel):
    """One hourly-wage bracket in the domestic INPS flat-rate table.

    ``hourly_rate_up_to`` is inclusive; ``None`` on the last entry means
    unbounded (covers any wage above the preceding bracket's threshold).
    """

    model_config = ConfigDict(extra="forbid")

    hourly_rate_up_to: Decimal | None
    employee_per_hour: NonNegativeRate
    employer_per_hour: NonNegativeRate
    employer_per_hour_fixed_term: NonNegativeRate
    provenance: RuleProvenance | None = None


class DomesticInpsRates(BaseModel):
    """Flat per-hour INPS contribution table for lavoro domestico.

    The selector is two-dimensional (INPS Circ. 9/2026, table 1):
    * ``weekly_hours > weekly_hours_threshold`` → use ``hours_bracket``,
      regardless of the worker's actual wage.
    * otherwise → walk ``wage_brackets`` in ascending ``hourly_rate_up_to``
      order and use the first bracket whose threshold is not exceeded.

    ``wage_brackets`` must be non-empty and end with one entry whose
    ``hourly_rate_up_to`` is ``None`` (the open-ended top bracket).
    """

    model_config = ConfigDict(extra="forbid")

    weekly_hours_threshold: int = Field(ge=0)
    hours_bracket: DomesticInpsHoursBracket
    wage_brackets: list[DomesticInpsWageBracket] = Field(min_length=1)
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _check_wage_brackets(self) -> Self:
        for i, bracket in enumerate(self.wage_brackets[:-1]):
            if bracket.hourly_rate_up_to is None:
                msg = (
                    f"DomesticInpsRates: wage_brackets[{i}] has "
                    "hourly_rate_up_to=None but is not the last bracket"
                )
                raise ValueError(msg)
            nxt = self.wage_brackets[i + 1].hourly_rate_up_to
            if nxt is not None and nxt <= bracket.hourly_rate_up_to:
                msg = (
                    "DomesticInpsRates: wage_brackets must have strictly "
                    f"ascending hourly_rate_up_to: bracket {i} = "
                    f"{bracket.hourly_rate_up_to} >= bracket {i + 1} = {nxt}"
                )
                raise ValueError(msg)
        last = self.wage_brackets[-1]
        if last.hourly_rate_up_to is not None:
            msg = (
                "DomesticInpsRates: last wage_bracket must have "
                f"hourly_rate_up_to=None (open-ended), "
                f"got {last.hourly_rate_up_to!r}"
            )
            raise ValueError(msg)
        return self


class InpsRawRates(BaseModel):
    """Raw INPS block from the tax JSON file, before tier resolution.

    ``employee_additional_rate`` and ``employee_additional_threshold`` are
    optional; both must be present together (validated by the loader).  When
    absent, the additional contribution is not modelled for this sector.

    ``employee_additional_threshold`` must be non-negative; a negative
    threshold would incorrectly widen the base on which the additional
    rate applies.

    ``employee_tiers`` and ``employer_tiers`` must be non-empty; an empty
    list would cause ``_resolve_tier`` to raise with no tier available for
    any headcount, which is a structural defect better caught at load time.
    """

    model_config = ConfigDict(extra="forbid")

    employee_tiers: list[InpsEmployeeTier] = Field(min_length=1)
    employer_tiers: list[InpsEmployerTier] = Field(min_length=1)
    ceiling: PositiveCeiling | None
    employee_additional_rate: NonNegativeRate | None = None
    employee_additional_threshold: NonNegativeRate | None = None
    provenance: RuleProvenance | None = None


class ApprenticeRawRates(BaseModel):
    """Raw apprentice block from the tax JSON file, before headcount resolution."""

    model_config = ConfigDict(extra="forbid")

    employee_rate: NonNegativeRate
    employee_ivs_rate: NonNegativeRate
    employer_rate: NonNegativeRate
    employer_ivs_rate: NonNegativeRate
    small_firm_max_employees: int = Field(ge=0)
    small_firm_employer_rate_months_0_11: NonNegativeRate
    small_firm_employer_ivs_rate_months_0_11: NonNegativeRate
    small_firm_employer_rate_months_12_23: NonNegativeRate
    small_firm_employer_ivs_rate_months_12_23: NonNegativeRate
    provenance: RuleProvenance | None = None

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
            assert_ivs_le_total(ivs_name, ivs_val, total_name, total_val)
        return self
