"""Compensation, allowance, and level models for CCNL contracts."""

from datetime import date
from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.agreement.validity.rules import TimeSeries
from ccnl_engine.compensation.accrual_comparison.models import (
    AccrualComparison as AccrualComparison,  # noqa: PLC0414
)
from ccnl_engine.compensation.allowance.models import Allowance as Allowance  # noqa: PLC0414
from ccnl_engine.compensation.cohort.models import ClassTable, CohortSalary
from ccnl_engine.compensation.entry.models import TransitionHireBand
from ccnl_engine.compensation.equalisation.models import EqualisationElement
from ccnl_engine.compensation.fixed_term.models import FixedTermPay
from ccnl_engine.compensation.hourly.models import HourlyPay
from ccnl_engine.compensation.loyalty.models import LoyaltyPremium
from ccnl_engine.compensation.presence.models import DailyPresenceAllowance
from ccnl_engine.compensation.renewal_minimum.models import RenewalAgreement
from ccnl_engine.compensation.una_tantum.models import UnaTantum
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.extra_month.offset.models import FourteenthPriorExtraOffset
from ccnl_engine.fund.assistance.models import AssistanceContribution
from ccnl_engine.fund.health.models import ContractualFund
from ccnl_engine.fund.models import (
    ContractualFundContribution,
    EmployerFund,
)
from ccnl_engine.fund.solidarity.models import SolidarityFund
from ccnl_engine.provenance.source.rule.models import ProvenanceStatus, RuleProvenance
from ccnl_engine.seniority.models import SeniorityIncrements

_SHORTEST_MONTH_DAYS = 28


class ExtraMonthAccrualRule(BaseModel):
    """When a month of an extra-month accrual window counts as a whole month.

    The CCNL clause on the ratei of the tredicesima and quattordicesima: a
    fraction of a month counts as a whole month when its days compare with
    ``min_days`` as ``comparison`` says, or, for the day-based comparisons,
    accrues its days.  The field is stored only
    when the signed text states it; without it the engine applies its
    default and the provenance inventory reports the rule as ``missing``.

    Attributes:
        min_days: Threshold in calendar days; ``None`` for a day-based
            comparison, which has none.
        comparison: How a month is counted (:class:`AccrualComparison`).
        working_days: The threshold counts the accruing days from Monday
            to Saturday instead of calendar days (CCNL Cooperative sociali
            art. 79: "superiore ai 15 giorni lavorativi", the week counted
            on six days by art. 60).
        provenance: Source of the clause; ``missing`` is not allowed, a
            rule without a source is left out of the data instead.
        valid_from: First day the clause applies, when a renewal changed
            it; the months starting before it follow :attr:`previous`.
        previous: The clause of the months before :attr:`valid_from`.

    Raises:
        ValueError: When a full 28-day month would not count, when the
            threshold is below one day, when a threshold is set or left out
            against the comparison, or when the provenance is ``missing``.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    min_days: int | None = None
    comparison: AccrualComparison
    working_days: bool = False
    provenance: RuleProvenance
    valid_from: date | None = None
    previous: "ExtraMonthAccrualRule | None" = None

    @model_validator(mode="after")
    def _check_threshold(self) -> Self:
        if self.provenance.status is ProvenanceStatus.MISSING:
            msg = "a stored accrual rule needs a source; omit it when missing"
            raise ValueError(msg)
        days = self.min_days
        if self.comparison.by_days:
            if days is not None or self.working_days:
                msg = f"{self.comparison.value}: omit min_days and working_days"
                raise ValueError(msg)
            return self
        more_than = self.comparison is AccrualComparison.MORE_THAN
        lowest, highest = (0, 27) if more_than else (1, _SHORTEST_MONTH_DAYS)
        if days is None or not lowest <= days <= highest:
            msg = (
                f"min_days must be between {lowest} and {highest} for "
                f"{self.comparison.value!r}; got {days}"
            )
            raise ValueError(msg)
        return self


class PaymentDay(BaseModel):
    """Calendar day on which the CCNL pays an extra month.

    Attributes:
        month: Month of the payment, 1-12.
        day: Day of the month, 1-28 so that every month has it.
        provenance: Source of the clause; ``missing`` is not allowed, a
            day without a source is left out of the data instead.

    Raises:
        ValueError: When the provenance is ``missing``.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    month: int = Field(ge=1, le=12)
    day: int = Field(ge=1, le=28)
    provenance: RuleProvenance

    @model_validator(mode="after")
    def _check_source(self) -> Self:
        if self.provenance.status is ProvenanceStatus.MISSING:
            msg = "a stored payment day needs a source; omit it when missing"
            raise ValueError(msg)
        return self


class RaccordoElement(BaseModel):
    """Frozen annual amount the CCNL pays with the tredicesima.

    The Elemento di Raccordo Contrattuale of the CCNL grafici editoriali
    (renewal of 19 January 2021): an amount per worker, stated by
    ``Employment.erc_amount``, that accrues by month as the tredicesima
    and has "alcuna incidenza su alcun istituto contrattuale o di legge".
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    provenance: RuleProvenance


class CCNLParameters(BaseModel):
    """Contract-wide parameters.

    ``accrual_rule``: month threshold of an extra-month window; ``*_payment_day``: their
    pay days; ``additional_months_by_category``: the payments of a category.
    ``flat_pay_max_weekly_hours``: hours at the full minimum (domestic: 30);
    ``solidarity_fund``: D.Lgs. 148/2015 art. 26; ``raccordo_element``: ERC;
    ``enam_levels``: ex ENAM; ``renewals``: raising the minimo (L. 199/2025);
    ``health_funds``, with their elemento distinto; ``hourly_pay``,
    ``fixed_term_pay`` (operai edilizia, OTD); ``loyalty_premium`` (fedeltà).
    ``daily_presence_allowances``: rates paid per counted qualifying day,
    rather than a fraction of monthly pay; ``meal_benefit_daily``: the
    non-remunerative meal voucher value per eligible day.
    ``equalisation_element`` retains the legacy single yearly element;
    ``equalisation_elements`` adds other yearly elements without replacing it.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    hourly_divisor: TimeSeries
    additional_months: TimeSeries
    fourteenth_prior_extra_offset: FourteenthPriorExtraOffset | None = None
    additional_months_by_category: dict[WorkerCategory, TimeSeries] = Field(
        default_factory=dict
    )
    seniority_increments: SeniorityIncrements
    seniority_increments_by_subsector: dict[str, SeniorityIncrements] = Field(
        default_factory=dict
    )
    employer_funds: tuple[EmployerFund, ...] = Field(default=())
    accrual_rule: ExtraMonthAccrualRule | None = None
    thirteenth_payment_day: PaymentDay | None = None
    fourteenth_payment_day: PaymentDay | None = None
    assistance_contribution: AssistanceContribution | None = None
    flat_pay_max_weekly_hours: int | None = Field(default=None, ge=1)
    contractual_fund_contribution: ContractualFundContribution | None = None
    raccordo_element: RaccordoElement | None = None
    enam_levels: tuple[str, ...] = ()
    solidarity_fund: SolidarityFund | None = None
    hourly_pay: HourlyPay | None = None
    fixed_term_pay: FixedTermPay | None = None
    renewals: tuple[RenewalAgreement, ...] = ()
    health_funds: tuple[ContractualFund, ...] = ()
    una_tantum: tuple[UnaTantum, ...] = ()
    equalisation_element: EqualisationElement | None = None
    equalisation_elements: tuple[EqualisationElement, ...] = ()
    loyalty_premium: LoyaltyPremium | None = None
    daily_presence_allowances: tuple[DailyPresenceAllowance, ...] = ()
    meal_benefit_daily: TimeSeries | None = None

    @model_validator(mode="after")
    def _check_positive_params(self) -> Self:
        """Reject a non-positive hourly_divisor or additional_months: both divide.

        Returns:
            The validated instance.

        Raises:
            ValueError: If any non-gap period in either series has value <= 0.
        """
        for field_name, series in (
            ("hourly_divisor", self.hourly_divisor),
            ("additional_months", self.additional_months),
        ):
            for p in series.periods:
                if p.value is not None and p.value <= 0:
                    msg = (
                        f"{field_name} values must be > 0; "
                        f"period starting {p.valid_from} has value {p.value}"
                    )
                    raise ValueError(msg)
        return self


class Level(BaseModel):
    """A single classification level (*livello di inquadramento*).

    The ``base_salary`` series records the contractual minimum, not the
    worker's complete ordinary remuneration. An individual element may
    supplement it without changing the level minimum. Likewise, a
    role-dependent qualified-worker floor can require a distinct allowance
    rather than rewriting the minimum shared by every worker in the level.
    Such pay is represented in the calculated pay chain, not in this table.

    Attributes:
        code, order, description: Code (``"D3"``), rank (1 = lowest), name.
        base_salary: Time-series of monthly base salaries for this level.
        base_salary_by_subsector, subsectors: Sub-sector pay and eligibility.
        base_salary_by_cohort, class_tables: Hired-worker or seniority-class tables.
        transition_to, transition_after_months, transition_hire_bands,
            transition_by: Entry promotion.
        fixed_allowances, category: Fixed allowances and optional worker category.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    order: int
    description: str
    base_salary: TimeSeries
    base_salary_by_subsector: dict[str, TimeSeries] = Field(default_factory=dict)
    base_salary_by_cohort: tuple[CohortSalary, ...] = ()
    class_tables: tuple[ClassTable, ...] = ()
    subsectors: tuple[str, ...] = ()
    fixed_allowances: tuple[Allowance, ...] = Field(default=())
    category: WorkerCategory | None = None
    transition_to: str | None = None
    transition_after_months: int | None = Field(default=None, gt=0)
    transition_hire_bands: tuple[TransitionHireBand, ...] = ()
    transition_by: date | None = None
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _check_salary_non_decreasing(self) -> Self:
        values: list[Decimal] = [
            p.value for p in self.base_salary.periods if p.value is not None
        ]
        for i in range(len(values) - 1):
            if values[i + 1] < values[i]:
                msg = (
                    f"base_salary must be non-decreasing over time: "
                    f"period {i} value {values[i]} > "
                    f"period {i + 1} value {values[i + 1]}"
                )
                raise ValueError(msg)
        return self
