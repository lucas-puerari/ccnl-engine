"""Compensation, allowance, and level models for CCNL contracts."""

from decimal import Decimal
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.contract.domain.assistance import AssistanceContribution
from ccnl_engine.contract.domain.category import WorkerCategory
from ccnl_engine.contract.domain.seniority import SeniorityIncrements
from ccnl_engine.contract.domain.validity import TimeSeries
from ccnl_engine.provenance.domain.chain import ProvenanceStatus, RuleProvenance


class Allowance(BaseModel):
    """A named fixed monthly allowance attached to a CCNL level.

    ``role`` restricts the allowance to workers holding that role (``None``
    means every worker at the level). ``months_per_year`` overrides the
    contract-wide ``additional_months`` for this allowance only. The three
    relevance flags exclude the allowance from the TFR base, the contribution
    base, or the apprenticeship-percentage base respectively.
    ``apprenticeship_pct_relevant=False`` means the allowance is paid at full
    value even for percentage-based apprentices (e.g. the EDR, which Italian
    CCNL commonly leave out of the elements the apprenticeship percentage
    applies to).  The default ``True`` reduces the allowance by the
    percentage together with the base salary; a CCNL that lists the reduced
    elements exempts every allowance it does not list.

    ``service_months_threshold`` makes the allowance conditional: it is
    included only when the recognised seniority (``Employment.seniority``)
    is known and is at least this many months on the run. When the
    seniority is unknown, threshold-gated allowances are excluded and the
    run names the missing fact: the engine cannot gate on service time
    without knowing service time.

    ``part_time_proportionable=False`` marks allowances that must be paid at
    their full contractual value regardless of the worker's part-time fraction
    (e.g. fixed-amount welfare contributions or presence-based indennità that
    Italian CCNL explicitly exclude from proportional reduction). Defaults to
    ``True`` so all existing allowances remain proportionable.

    ``in_kind=True`` marks the conventional value of a benefit the employer
    provides in kind (the board and lodging of a live-in domestic worker,
    CCNL lavoro domestico art. 36): a regular run pays no cash for it but
    counts it in the TFR base, and an extra-month run pays it in cash.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    description: str
    monthly: TimeSeries
    role: str | None = None
    months_per_year: int | None = Field(default=None, ge=1)
    tfr_relevant: bool = True
    contribution_relevant: bool = True
    apprenticeship_pct_relevant: bool = True
    part_time_proportionable: bool = True
    in_kind: bool = False
    service_months_threshold: int | None = Field(default=None, ge=0)
    provenance: RuleProvenance | None = None

    @property
    def apprenticeship_pct_declared(self) -> bool:
        """Whether the data states ``apprenticeship_pct_relevant``.

        ``False`` when the flag holds its default: whether the CCNL reduces
        the allowance for percentage apprentices was not sourced.
        """
        return "apprenticeship_pct_relevant" in self.model_fields_set


class FundContributionBase(StrEnum):
    """Pay the rates of a contractual fund are computed on.

    Attributes:
        INPS_BASE: The INPS contribution base of the run (gross minus the
            allowances excluded from contributions).
        TFR_BASE: The pay counted for the TFR of the run (*retribuzione
            utile ai fini del TFR*, art. 2120 c.c.): the gross minus the
            allowances excluded from the TFR, with the TFR-relevant events.
    """

    INPS_BASE = "inps_base"
    TFR_BASE = "tfr_base"


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
    categories (``None`` = all).
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


class AccrualComparison(StrEnum):
    """How the accruing days of a month are compared with the threshold.

    Attributes:
        AT_LEAST: The month counts when its days reach the threshold
            ("pari o superiore a 15 giorni").
        MORE_THAN: The month counts when its days exceed the threshold
            ("frazione superiore a 15 giorni").
    """

    AT_LEAST = "at_least"
    MORE_THAN = "more_than"


_SHORTEST_MONTH_DAYS = 28


class ExtraMonthAccrualRule(BaseModel):
    """When a month of an extra-month accrual window counts as a whole month.

    The CCNL clause on the ratei of the tredicesima and quattordicesima: a
    fraction of a month counts as a whole month when its days compare with
    ``min_days`` as ``comparison`` says.  The field is stored only when the
    signed text states it; without it the engine applies its default and
    the provenance inventory reports the rule as ``missing``.

    Attributes:
        min_days: Threshold in calendar days.
        comparison: ``at_least`` or ``more_than``.
        provenance: Source of the clause; ``missing`` is not allowed, a
            rule without a source is left out of the data instead.

    Raises:
        ValueError: When a full 28-day month would not count, when the
            threshold is below one day, or when the provenance is
            ``missing``.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    min_days: int
    comparison: AccrualComparison
    provenance: RuleProvenance

    @model_validator(mode="after")
    def _check_threshold(self) -> Self:
        more_than = self.comparison is AccrualComparison.MORE_THAN
        lowest, highest = (0, 27) if more_than else (1, _SHORTEST_MONTH_DAYS)
        if not lowest <= self.min_days <= highest:
            msg = (
                f"min_days must be between {lowest} and {highest} for "
                f"{self.comparison.value!r}; got {self.min_days}"
            )
            raise ValueError(msg)
        if self.provenance.status is ProvenanceStatus.MISSING:
            msg = "a stored accrual rule needs a source; omit it when missing"
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


class CCNLParameters(BaseModel):
    """Contract-wide parameters.

    ``accrual_rule`` is the CCNL threshold for counting a month of an
    extra-month window, ``None`` when the bundle has no sourced clause.
    ``thirteenth_payment_day`` and ``fourteenth_payment_day`` are the days
    the CCNL pays the tredicesima and the quattordicesima, ``None`` when the
    bundle has no sourced clause.
    ``assistance_contribution`` is the contribution the CCNL charges per
    paid hour, ``None`` when it charges none.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    hourly_divisor: TimeSeries
    additional_months: TimeSeries
    seniority_increments: SeniorityIncrements
    employer_funds: tuple[EmployerFund, ...] = Field(default=())
    accrual_rule: ExtraMonthAccrualRule | None = None
    thirteenth_payment_day: PaymentDay | None = None
    fourteenth_payment_day: PaymentDay | None = None
    assistance_contribution: AssistanceContribution | None = None

    @model_validator(mode="after")
    def _check_positive_params(self) -> Self:
        """Reject non-positive hourly_divisor or additional_months values.

        Both parameters appear in the denominator of hourly-rate and monthly
        pay calculations; a zero or negative value would produce nonsensical
        results and is always a data-entry error.

        Returns:
            The validated instance (required by Pydantic model_validator).

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

    Attributes:
        code: Short alphanumeric code identifying the level within the CCNL
            (e.g. ``"D3"``, ``"A1"``). Used in ``Scenario.level_code``.
        order: Numeric ranking from lowest to highest seniority/pay (1 = lowest).
            Used by ``CCNL.level_by_order``.
        description: Human-readable name of the classification level.
        base_salary: Time-series of monthly base salaries for this level.
        fixed_allowances: List of fixed monthly allowances attached to the
            level (e.g. EDR, contingenza). May be empty.
        category: Worker category fixed by this level. ``None`` when the
            level hosts more than one category; the category then comes from
            the employment facts (``Employment.category``).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    order: int
    description: str
    base_salary: TimeSeries
    fixed_allowances: tuple[Allowance, ...] = Field(default=())
    category: WorkerCategory | None = None
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _check_salary_non_decreasing(self) -> Self:
        # Compare only adjacent non-gap periods; gap periods carry no value.
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
