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
from ccnl_engine.contract.domain.identity import PublicPensionFund
from ccnl_engine.provenance.domain.chain import RuleProvenance
from ccnl_engine.shared.domain.primitives import (
    NonNegativeRate,
    PositiveCeiling,
    assert_ivs_le_total,
)
from ccnl_engine.tax.domain.additional_ivs import AdditionalIvsRule
from ccnl_engine.tax.domain.fis_reduction import FisReduction
from ccnl_engine.tax.domain.minimum_base import MinimumBaseRule


class EndOfServiceRates(BaseModel):
    """Contributions to the end-of-service fund of INPS Gestione Dipendenti Pubblici.

    ENPAS for the employees of the State (DPR 1032/1973 artt. 37-38: 80% of
    the "stipendio, paga o retribuzione annui", the tredicesima left out),
    INADEL for those of the enti locali and of the health service (L.
    152/1968 art. 11: 80% of the pay, the tredicesima included).  Under the
    TFS the worker pays ``tfs_employee_rate`` and the administration
    ``tfs_employer_rate``; under the TFR at INPS the administration pays
    ``tfr_employer_rate`` and the gross is reduced by ``tfs_employee_rate``
    (DPCM 20 dicembre 1999 art. 1 cc. 2-3).

    Attributes:
        base_share: Share of the pay that forms the contribution base.
        tfs_employee_rate: Rate of the worker under the TFS.
        tfs_employer_rate: Rate of the administration under the TFS.
        tfr_employer_rate: Rate of the administration under the TFR.
        thirteenth: Whether the tredicesima forms part of the base.
        provenance: Source of the rates.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    base_share: NonNegativeRate
    tfs_employee_rate: NonNegativeRate
    tfs_employer_rate: NonNegativeRate
    tfr_employer_rate: NonNegativeRate
    thirteenth: bool
    provenance: RuleProvenance | None = None


class PublicCreditRate(BaseModel):
    """Contribution of a public employee to the Gestione unitaria del credito.

    L. 662/1996 art. 1 cc. 242-243: "Il contributo obbligatorio per il
    credito [...] è pari allo 0,35 per cento della retribuzione contributiva
    e pensionabile", owed by the members of every fund of the Gestione
    Dipendenti Pubblici.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    employee_rate: NonNegativeRate
    provenance: RuleProvenance | None = None


class PublicLifeInsuranceRates(BaseModel):
    """Rates of the Assicurazione Sociale Vita (ex ENPDEP) of a public employee.

    INPS circ. 104/2014 par. 3.1: "la base imponibile è costituita dalla
    retribuzione pensionabile [...] Il contributo è pari allo 0,12% della
    base imponibile e grava in misura pari allo 0,027% sul lavoratore ed
    allo 0,093% sul datore di lavoro".
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    employee_rate: NonNegativeRate
    employer_rate: NonNegativeRate
    provenance: RuleProvenance | None = None


class PublicEnamRate(BaseModel):
    """Contribution of a teacher to the Gestione Assistenza Magistrale (ex ENAM).

    L. 93/1957 art. 3 c. 1 lett. a: the permanent teachers of the scuola
    dell'infanzia and primaria pay 1% of 80% of the stipendio; the INPS
    table lists "ENAM 1 -- 1".
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    employee_rate: NonNegativeRate
    base_share: NonNegativeRate
    provenance: RuleProvenance | None = None


class PublicFundRates(BaseModel):
    """Pension contribution rates of a fund of INPS Gestione Dipendenti Pubblici.

    The whole rate is IVS: the Gestione pays pensions alone.
    ``end_of_service`` is the end-of-service fund of its members.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    employee_rate: NonNegativeRate
    employer_rate: NonNegativeRate
    provenance: RuleProvenance | None = None
    end_of_service: EndOfServiceRates | None = None


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

    ``employee_additional`` is the 1% IVS charged to the worker on the pay
    above the first pensionable band (art. 3-ter D.L. 384/1992), see
    :class:`~ccnl_engine.tax.domain.additional_ivs.AdditionalIvsRule`; it is
    applied on top of the ordinary rate and, being IVS, within the massimale
    when ``ivs_ceiling_applies`` is True.  ``None`` when the sector does not
    model it.

    ``minimum_base`` is the minimale the INPS base of a run is raised to,
    see :class:`~ccnl_engine.tax.domain.minimum_base.MinimumBaseRule`;
    ``None`` when the sector does not model it.

    ``ceiling_provenance`` backs the massimale, read from another source
    than the rates; ``fis_reduction`` is the cut of the FIS rate of the
    smallest employers (:mod:`~ccnl_engine.tax.domain.fis_reduction`), and
    ``fis_reduction_open`` flags rates resolved for an employer it may
    apply to that does not say whether it does.
    """

    model_config = ConfigDict(extra="forbid")

    employee_rate: NonNegativeRate
    employee_ivs_rate: NonNegativeRate
    employer_rate: NonNegativeRate
    employer_ivs_rate: NonNegativeRate
    ceiling: PositiveCeiling | None
    employer_rate_by_category: dict[WorkerCategory, NonNegativeRate] = {}
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
    fis_reduction_open: bool = False

    @property
    def ceiling_record(self) -> RuleProvenance | None:
        """The record of the massimale: its own, else that of the rates."""
        return self.ceiling_provenance or self.provenance

    def for_public_fund(self, fund: PublicPensionFund | None) -> InpsRates:
        """Return the rates of a fund of the Gestione Dipendenti Pubblici.

        Returns:
            These rates with the pension rates of ``fund`` when the year
            gives them apart, else these rates (the tiers hold the CTPS).
        """
        rates = None if fund is None else self.public_funds.get(fund)
        if rates is None:
            return self
        return self.model_copy(
            update={
                "employee_rate": rates.employee_rate,
                "employee_ivs_rate": rates.employee_rate,
                "employer_rate": rates.employer_rate,
                "employer_ivs_rate": rates.employer_rate,
                "provenance": rates.provenance,
                "end_of_service": rates.end_of_service,
            }
        )

    @model_validator(mode="after")
    def _check_rates(self) -> Self:
        """Enforce the IVS <= total invariants (``ValueError`` otherwise).

        Returns:
            The validated instance.
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
