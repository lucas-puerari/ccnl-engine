"""Raw INPS contribution blocks of the data files, keyed by headcount tier.

The loader resolves them for one employer headcount into the flat rates of
:mod:`~ccnl_engine.tax.contribution.models`.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.contract.employment.models_category import WorkerCategory
from ccnl_engine.contract.identity.facade import PublicPensionFund
from ccnl_engine.primitives import (
    NonNegativeRate,
    PositiveCeiling,
    assert_ivs_le_total,
)
from ccnl_engine.provenance.source.models_chain import RuleProvenance
from ccnl_engine.tax.contribution.models import (
    EndOfServiceRates,
    PublicCreditRate,
    PublicEnamRate,
    PublicFundRates,
    PublicLifeInsuranceRates,
)
from ccnl_engine.tax.contribution.models_additional_ivs import AdditionalIvsRule
from ccnl_engine.tax.contribution.models_fis_reduction import FisReduction
from ccnl_engine.tax.contribution.models_minimum_base import MinimumBaseRule
from ccnl_engine.tax.contribution.models_zone_reduction import ZoneReduction


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
    fixed_term_rate_by_category: dict[WorkerCategory, NonNegativeRate] = {}
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _check_ivs_rate(self) -> Self:
        assert_ivs_le_total("ivs_rate", self.ivs_rate, "rate", self.rate)
        rates = {**self.rate_by_category, **self.fixed_term_rate_by_category}
        for cat, cat_rate in rates.items():
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

    ``employee_additional`` is optional: when absent, the additional 1% IVS
    is not modelled for this sector.  ``minimum_base`` is the minimale of
    the year; when absent, the INPS base is never raised to a minimum.
    ``public_funds`` are the rates of the funds of the Gestione Dipendenti
    Pubblici other than the tiers, by fund (``CCNLMeta.public_pension_fund``);
    ``end_of_service`` the end-of-service fund of the tiers (ENPAS).
    ``ceiling_provenance`` backs the massimale apart from the rates;
    ``fis_reduction`` is the cut of the FIS rate of the smallest employers.
    ``base_whole_euro`` rounds the base of a run to the whole euro (INPS
    circ. 208/2001, the denunce of private employers); the Gestione
    Dipendenti Pubblici keeps it to the cent.

    ``employee_tiers`` and ``employer_tiers`` must be non-empty; an empty
    list would cause ``_resolve_tier`` to raise with no tier available for
    any headcount, which is a structural defect better caught at load time.
    """

    model_config = ConfigDict(extra="forbid")

    employee_tiers: list[InpsEmployeeTier] = Field(min_length=1)
    employer_tiers: list[InpsEmployerTier] = Field(min_length=1)
    ceiling: PositiveCeiling | None
    employee_additional: AdditionalIvsRule | None = None
    minimum_base: MinimumBaseRule | None = None
    provenance: RuleProvenance | None = None
    public_funds: dict[PublicPensionFund, PublicFundRates] = {}
    end_of_service: EndOfServiceRates | None = None
    public_credit: PublicCreditRate | None = None
    public_life_insurance: PublicLifeInsuranceRates | None = None
    public_enam: PublicEnamRate | None = None
    ceiling_provenance: RuleProvenance | None = None
    fis_reduction: FisReduction | None = None
    base_whole_euro: bool = True
    zone_reduction: ZoneReduction | None = None


class ApprenticeHeadcountShare(BaseModel):
    """Non-IVS shares an apprentice owes on top of the statutory rates.

    Since 1 January 2022 apprentices pay the wage-integration contributions
    of their employer (D.Lgs. 148/2015 art. 2; INPS circ. 76/2022 par. 1):
    CIGO, CIGS or FIS, whose rates depend on the headcount.  Each share is
    added to every employer period (reduced small-firm years included) and
    to the employee rate; none of it is IVS, so it is never capped.

    Attributes:
        max_employees: Largest headcount of the tier; ``None`` is the open
            tier.
        employer_rate: Employer share added to the apprentice employer rates.
        employee_rate: Worker share added to the apprentice employee rate.
    """

    model_config = ConfigDict(extra="forbid")

    max_employees: int | None
    employer_rate: NonNegativeRate
    employee_rate: NonNegativeRate


class ApprenticeRawRates(BaseModel):
    """Raw apprentice block from the tax JSON file, before headcount resolution.

    ``headcount_shares`` are the wage-integration shares by headcount tier;
    empty when the sector owes none to INPS.
    """

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
    headcount_shares: list[ApprenticeHeadcountShare] = []
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
