"""CCNL domain models."""

from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Literal, Self

from pydantic import BaseModel, Field, model_validator

from ccnl_engine.models.apprenticeship import Apprenticeship
from ccnl_engine.models.validity import TimeSeries


class TaxSector(StrEnum):
    """INPS sector classification used to select the contribution-rate file."""

    TERZIARIO = "terziario"
    INDUSTRIA = "industria"
    ARTIGIANATO = "artigianato"
    EDILIZIA = "edilizia"


class Allowance(BaseModel):
    """A named fixed monthly allowance attached to a CCNL level."""

    code: str
    description: str
    monthly: TimeSeries


class SeniorityIncrements(BaseModel):
    """Seniority increment (*scatti di anzianità*) rules for a CCNL."""

    cadence_months: int
    maximum_count: int
    amount_by_level: dict[str, TimeSeries]


class Parameters(BaseModel):
    """Contract-wide parameters."""

    hourly_divisor: int
    additional_months: TimeSeries
    seniority_increments: SeniorityIncrements


class Level(BaseModel):
    """A single classification level (*livello di inquadramento*)."""

    code: str
    order: int
    description: str
    base_salary: TimeSeries
    fixed_allowances: list[Allowance] = []

    @model_validator(mode="after")
    def _check_salary_non_decreasing(self) -> Self:
        periods = self.base_salary.periods
        for i in range(len(periods) - 1):
            if periods[i + 1].value < periods[i].value:
                msg = (
                    f"base_salary must be non-decreasing over time: "
                    f"period {i} value {periods[i].value} > "
                    f"period {i + 1} value {periods[i + 1].value}"
                )
                raise ValueError(msg)
        return self


class Coverage(BaseModel):
    """Declares implementation status for a CCNL data file."""

    layer_1: Literal["implemented", "partial", "out_of_scope"]
    layer_2: Literal["implemented", "partial", "out_of_scope"]
    layer_3: Literal["implemented", "partial", "out_of_scope"]
    notes: list[str]


class CCNLSource(BaseModel):
    """A primary source reference for a CCNL data file."""

    url: str
    type: str
    agreement_date: str | None = None


class CCNLExtraction(BaseModel):
    """Metadata about how the CCNL data was extracted."""

    method: str
    model: str | None = None
    timestamp: str
    human_reviewed: bool


class CCNLMeta(BaseModel):
    """Identifying metadata for a CCNL."""

    id: str
    name: str
    cnel_code: str
    sector: str
    tax_sector: TaxSector
    signatories: list[str]
    sources: list[CCNLSource]
    extraction: CCNLExtraction


class CCNL(BaseModel):
    """Root model for a CCNL data file."""

    schema_version: str
    ccnl: CCNLMeta
    parameters: Parameters
    levels: list[Level]
    apprenticeship: Annotated[
        Apprenticeship,
        Field(description="Apprenticeship rules for this CCNL."),
    ]
    coverage: Coverage

    @model_validator(mode="after")
    def _validate_cross_fields(self) -> Self:
        self._assert_unique_orders()
        self._assert_unique_codes()
        self._assert_seniority_level_codes()
        self._assert_salary_order_non_decreasing()
        return self

    def _assert_unique_orders(self) -> None:
        orders = [lv.order for lv in self.levels]
        if len(orders) != len(set(orders)):
            msg = f"level order values must be unique, got: {orders}"
            raise ValueError(msg)

    def _assert_unique_codes(self) -> None:
        codes = [lv.code for lv in self.levels]
        if len(codes) != len(set(codes)):
            msg = f"level code values must be unique, got: {codes}"
            raise ValueError(msg)

    def _assert_seniority_level_codes(self) -> None:
        existing = {lv.code for lv in self.levels}
        for code in self.parameters.seniority_increments.amount_by_level:
            if code not in existing:
                msg = (
                    f"seniority_increments references level code {code!r} "
                    f"which does not exist in levels"
                )
                raise ValueError(msg)

    def _assert_salary_order_non_decreasing(self) -> None:
        if len(self.levels) < 2:
            return
        sorted_levels = sorted(self.levels, key=lambda lv: lv.order)
        all_dates = _collect_transition_dates(sorted_levels)
        for check_date in sorted(all_dates):
            prev_value: Decimal | None = None
            prev_code: str = ""
            for lv in sorted_levels:
                try:
                    value = lv.base_salary.value_at(check_date)
                except ValueError:
                    continue
                if prev_value is not None and value < prev_value:
                    msg = (
                        f"salary ordering violated on {check_date}: "
                        f"level {lv.code!r} (order={lv.order}) "
                        f"earns {value} < level {prev_code!r} earns {prev_value}"
                    )
                    raise ValueError(msg)
                prev_value = value
                prev_code = lv.code


def _collect_transition_dates(levels: list[Level]) -> set[date]:
    all_dates: set[date] = set()
    for lv in levels:
        for period in lv.base_salary.periods:
            all_dates.add(period.valid_from)
    return all_dates
