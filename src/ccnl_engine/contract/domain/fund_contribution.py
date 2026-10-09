"""Contributions a CCNL sets to its funds: rates of an enrolment, fixed amounts."""

from decimal import Decimal
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.contract.domain.category import WorkerCategory
from ccnl_engine.contract.domain.validity import TimeSeries
from ccnl_engine.provenance.domain.chain import RuleProvenance


class FundContributionBase(StrEnum):
    """Pay the rates of a contractual fund are computed on.

    Attributes:
        INPS_BASE: The INPS contribution base of the run (gross minus the
            allowances excluded from contributions).
        TFR_BASE: The pay counted for the TFR of the run (*retribuzione
            utile ai fini del TFR*, art. 2120 c.c.): the gross minus the
            allowances excluded from the TFR, with the TFR-relevant events.
        CONTRACTUAL_MINIMUM: The contractual minimum of the level the run
            pays (*minimi contrattuali*, e.g. of Cometa): the base salary of
            the pay chain, prorated and scaled as the run pays it.
    """

    INPS_BASE = "inps_base"
    TFR_BASE = "tfr_base"
    CONTRACTUAL_MINIMUM = "contractual_minimum"


class EmployerRateTier(BaseModel):
    """Employer rate due once the worker contributes at least a rate.

    Attributes:
        employee_from: Least employee rate of the tier.
        rate: Employer rate of the tier.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    employee_from: Decimal = Field(ge=0, le=1)
    rate: TimeSeries


class EmployerFund(BaseModel):
    """An employer-side contribution to a contractual fund (e.g. a pension fund).

    ``rate`` is a fraction of the pay ``contribution_base`` names, as the
    engine computes it: the INPS contribution base (the default) or the TFR
    base.  A fund whose official rate is expressed on another base (e.g.
    the *imponibile Cassa Edile* or the minimum wage alone) is not stored
    with a rate.  ``employee_min_rate`` is the minimum employee contribution
    the CCNL sets on the same base, when the bundle records one.
    ``apprentice_rate`` is the employer rate for apprentices when the fund
    sets one apart (``None`` = ``rate``).
    ``applies_to_categories`` restricts the fund to levels of the given
    categories (``None`` = all).  ``employee_base_above_minimum`` is the
    base of an employee rate the worker chose above the minimum, when the
    fund sets one apart (Cometa: the TFR base).  ``young_member_rate`` is
    the employer rate of a member the CCNL favours for the age at enrolment
    (Cometa: enrolled after 5 February 2021 before turning 35), stated by
    ``PensionFundEnrolment.young_member``.  ``employer_rate_tiers`` raise
    the employer rate when the worker chooses a higher rate (Fondapi on the
    chemical PMI: 2.00% from an employee 1.60%); the highest tier reached
    replaces ``rate``.  ``extra_months`` is false when the contributions are
    due on the twelve monthly payments alone (Byblos on the CCNL Esercizi
    cinematografici, art. 43: "per 12 mensilità annue").
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    description: str
    rate: TimeSeries
    employee_min_rate: TimeSeries | None = None
    apprentice_rate: TimeSeries | None = None
    contribution_base: FundContributionBase = FundContributionBase.INPS_BASE
    applies_to_categories: tuple[WorkerCategory, ...] | None = None
    provenance: RuleProvenance | None = None
    employee_base_above_minimum: FundContributionBase | None = None
    young_member_rate: TimeSeries | None = None
    employer_rate_tiers: tuple[EmployerRateTier, ...] = ()
    extra_months: bool = True


class ContractualFundContribution(BaseModel):
    """Monthly employer contribution owed to a fund whatever the enrolment.

    Some CCNLs charge the employer a fixed amount a month per worker, which
    enrols the worker in the fund by contract (e.g. the 5 EUR "riparametrati
    sul base 100" the CCNL Materiali da costruzione owes Fondapi from 1
    January 2022).  It is an employer contribution to a pension fund: outside
    the INPS base with the 10% solidarity contribution and within the
    deduction cap of the worker's contributions.

    Attributes:
        code: Code of the fund it is paid to.
        description: Name of the fund.
        monthly_by_level: Amount a month for each level code, in EUR; a
            level without one is not covered by this model.
        provenance: Source of the clause.
        categories: Worker categories the amounts are for, ``None`` for
            all; another category (e.g. the operai the Prevedi pays per hour
            worked) is not covered by this model.
        apprentice_monthly: Amount a month of an apprentice, when the CCNL
            sets one apart.
        minimum_days_in_month: Calendar days worked in the month below
            which nothing is owed, sickness and days without pay left out
            (15 for Prevedi); ``None`` when the clause sets none.
        extra_months: Whether an extra-month run owes the amount in
            proportion to its ratei.
        part_time_proportional: Whether a part-time worker owes the amount
            in proportion to the weekly hours.
        minimum_fixed_term_months: A fixed-term employment that lasts no
            more than these months owes nothing; ``None`` when the clause
            sets no minimum.
        hourly_by_level: Amount per ordinary hour worked for each level, for
            the ``hourly_categories`` (Prevedi: the operai), rounded to the
            euro a month; ``apprentice_hourly`` the one of an apprentice.

    Raises:
        ValueError: When an amount is negative.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    description: str
    monthly_by_level: dict[str, TimeSeries]
    provenance: RuleProvenance
    categories: tuple[WorkerCategory, ...] | None = None
    apprentice_monthly: TimeSeries | None = None
    minimum_days_in_month: int | None = Field(default=None, ge=1, le=31)
    extra_months: bool = False
    part_time_proportional: bool = False
    minimum_fixed_term_months: int | None = Field(default=None, ge=1)
    hourly_by_level: dict[str, TimeSeries] | None = None
    hourly_categories: tuple[WorkerCategory, ...] | None = None
    apprentice_hourly: TimeSeries | None = None

    @model_validator(mode="after")
    def _check_non_negative(self) -> Self:
        for level, series in self.monthly_by_level.items():
            for period in series.periods:
                if period.value is not None and period.value < 0:
                    msg = (
                        f"monthly_by_level[{level}] must be >= 0; period "
                        f"starting {period.valid_from} has {period.value}"
                    )
                    raise ValueError(msg)
        return self
