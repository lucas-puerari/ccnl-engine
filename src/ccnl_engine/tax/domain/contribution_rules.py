"""Resolved INPS contribution rates, as the contribution engine reads them.

The raw tiered blocks they are resolved from live in
:mod:`~ccnl_engine.tax.domain.contribution_tiers`; the domestic-work table in
:mod:`~ccnl_engine.tax.domain.domestic_contribution_rules`.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator

from ccnl_engine.contract.domain.category import WorkerCategory
from ccnl_engine.provenance.domain.chain import RuleProvenance
from ccnl_engine.shared.domain.primitives import (
    NonNegativeRate,
    PositiveCeiling,
    assert_ivs_le_total,
)


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
