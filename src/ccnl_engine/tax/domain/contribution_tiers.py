"""Raw INPS contribution blocks of the data files, keyed by headcount tier.

The loader resolves them for one employer headcount into the flat rates of
:mod:`~ccnl_engine.tax.domain.contribution_rules`.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.contract.domain.category import WorkerCategory
from ccnl_engine.provenance.domain.chain import RuleProvenance
from ccnl_engine.shared.domain.primitives import (
    NonNegativeRate,
    PositiveCeiling,
    assert_ivs_le_total,
)


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
