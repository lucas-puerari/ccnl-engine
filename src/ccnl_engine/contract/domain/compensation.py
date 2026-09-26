"""Compensation, allowance, and level models for CCNL contracts."""

from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.contract.domain.category import WorkerCategory
from ccnl_engine.contract.domain.seniority import SeniorityIncrements
from ccnl_engine.contract.domain.validity import TimeSeries
from ccnl_engine.provenance.domain.chain import RuleProvenance


class Allowance(BaseModel):
    """A named fixed monthly allowance attached to a CCNL level.

    ``role`` restricts the allowance to workers holding that role (``None``
    means every worker at the level). ``months_per_year`` overrides the
    contract-wide ``additional_months`` for this allowance only. The three
    relevance flags exclude the allowance from the TFR base, the contribution
    base, or the apprenticeship-percentage base respectively.
    ``apprenticeship_pct_relevant=False`` means the allowance is paid at full
    value even for percentage-based apprentices (e.g. EDR per Art. 3 L.
    297/1982, which Italian CCNL commonly exempt from apprenticeship
    percentage reductions).

    ``service_months_threshold`` makes the allowance conditional: it is
    included only when ``Scenario.seniority_months`` is provided and is at
    least this many months. When ``Scenario.seniority_count`` is used instead
    of ``seniority_months``, threshold-gated allowances are excluded (the
    engine cannot gate on service time without knowing service time).

    ``part_time_proportionable=False`` marks allowances that must be paid at
    their full contractual value regardless of the worker's part-time fraction
    (e.g. fixed-amount welfare contributions or presence-based indennità that
    Italian CCNL explicitly exclude from proportional reduction). Defaults to
    ``True`` so all existing allowances remain proportionable.
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
    service_months_threshold: int | None = Field(default=None, ge=0)
    provenance: RuleProvenance | None = None


class EmployerFund(BaseModel):
    """An employer-side contribution to a contractual fund (e.g. Cassa Edile).

    ``rate`` is a fraction of the **INPS contribution base** (gross minus
    contribution-excluded allowances) as computed by the engine.  This is the
    same base used for INPS social-security contributions.  Note that some
    sector funds (notably Cassa Edile) are conventionally assessed on a
    different base (*imponibile Cassa Edile*); if the fund's official rate is
    expressed on that base, it must be adjusted to the INPS base before being
    stored here.  ``applies_to_categories`` restricts the fund to levels of the
    given categories (``None`` = all).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    description: str
    rate: TimeSeries
    applies_to_categories: tuple[WorkerCategory, ...] | None = None
    provenance: RuleProvenance | None = None


class CCNLParameters(BaseModel):
    """Contract-wide parameters."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    hourly_divisor: TimeSeries
    additional_months: TimeSeries
    seniority_increments: SeniorityIncrements
    employer_funds: tuple[EmployerFund, ...] = Field(default=())

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
