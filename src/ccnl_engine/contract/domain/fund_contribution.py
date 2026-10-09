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
        CONVENTIONAL: A fixed monthly base the fund applies to the worker,
            stated by ``PensionFundEnrolment.conventional_base``
            (Previambiente: the base pay of the level at 1 January 1997,
            its contingenza and one scatto).
    """

    INPS_BASE = "inps_base"
    TFR_BASE = "tfr_base"
    CONTRACTUAL_MINIMUM = "contractual_minimum"
    CONVENTIONAL = "conventional"


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
    replaces ``rate``.  ``erc_holder_rate`` is the employer rate of a worker
    who holds the Elemento di Raccordo Contrattuale of the CCNL grafici
    editoriali (Byblos: 1.4% instead of 1.9%), stated by
    ``Employment.erc_amount``.  ``extra_months`` is false when the contributions are
    due on the twelve monthly payments alone (Byblos on the CCNL Esercizi
    cinematografici, art. 43: "per 12 mensilità annue").
    ``enrolled_monthly`` is a fixed employer amount a month for a worker
    enrolled voluntarily, on the monthly payments the rates are due on
    (Previambiente: 22 EUR, 30.50 EUR from January 2027).  ``paid_month_only``
    is true when the rates and that amount are due only on the pay of the
    month: none for a month without pay; a month paid in part (an unpaid
    absence, sickness, a partial month) traverses the open limitation
    ``fund_paid_month`` the CCNL declares (Previambiente art. 65 c. 8).
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
    erc_holder_rate: TimeSeries | None = None
    enrolled_monthly: TimeSeries | None = None
    paid_month_only: bool = False

    def rate_series(self) -> tuple[tuple[str, TimeSeries | None], ...]:
        """Return the series of the fund a run may read, by key.

        Returns:
            The employer and employee rates, the rates of a young member
            and of an ERC holder, and the fixed amount of an enrolled one.
        """
        return (
            ("rate", self.rate),
            ("employee_min_rate", self.employee_min_rate),
            ("young_member_rate", self.young_member_rate),
            ("erc_holder_rate", self.erc_holder_rate),
            ("enrolled_monthly", self.enrolled_monthly),
        )


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
            in proportion to the weekly hours; ``None`` when the clause
            gives no rule (the full amount, with an open limitation).
        permanent_only: Whether a worker not enrolled voluntarily owes it
            only on a permanent contract or an apprenticeship (Previambiente
            art. 65 c. 11).
        not_enrolled_monthly: Amount a month added for a worker not enrolled
            voluntarily (Previambiente: the 10 EUR of c. 11, beside the 5
            EUR insurance of c. 13 every member owes).
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
    part_time_proportional: bool | None = None
    minimum_fixed_term_months: int | None = Field(default=None, ge=1)
    hourly_by_level: dict[str, TimeSeries] | None = None
    hourly_categories: tuple[WorkerCategory, ...] | None = None
    apprentice_hourly: TimeSeries | None = None
    permanent_only: bool = False
    not_enrolled_monthly: TimeSeries | None = None

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
