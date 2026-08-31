"""CCNL domain models.

The root model is :class:`CCNL`. All monetary values are
:class:`~ccnl_engine.models.validity.TimeSeries` objects; no bare
:class:`~decimal.Decimal` scalars appear at the CCNL level.
"""

from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Literal, Self

from pydantic import BaseModel, Field, model_validator

from ccnl_engine.models.apprenticeship import Apprenticeship
from ccnl_engine.models.validity import TimeSeries


class TaxSector(StrEnum):
    """INPS sector classification used to select the correct contribution rates.

    Each value maps to a ``tax/data/<year>-<value>.json`` file.  Add new
    values only when a corresponding data file is also added.

    Attributes:
        TERZIARIO: Commerce, distribution, services (Confcommercio, Confesercenti…).
        INDUSTRIA: Manufacturing / industry (Federmeccanica, Confindustria…).
        ARTIGIANATO: Craft trades (Confartigianato, CNA…).
    """

    TERZIARIO = "terziario"
    INDUSTRIA = "industria"
    ARTIGIANATO = "artigianato"


class Allowance(BaseModel):
    """A named fixed monthly allowance attached to a CCNL level.

    Attributes:
        code: Machine-readable identifier (e.g. ``"contingenza"``).
        description: Human-readable name.
        monthly: Monthly amount as a :class:`TimeSeries`.
    """

    code: str
    description: str
    monthly: TimeSeries


class SeniorityIncrements(BaseModel):
    """Seniority increment (*scatti di anzianità*) rules for a CCNL.

    Attributes:
        cadence_months: Number of months between increments (e.g. ``36``).
        maximum_count: Maximum number of increments an employee can accrue.
        amount_by_level: Map from level code to the monthly increment amount
            for that level, as a :class:`TimeSeries`.
    """

    cadence_months: int
    maximum_count: int
    amount_by_level: dict[str, TimeSeries]


class Parameters(BaseModel):
    """Contract-wide parameters.

    Attributes:
        hourly_divisor: Divisor used to compute the hourly rate from the
            monthly salary (e.g. ``168`` for 40 h/week contracts).
        additional_months: Number of monthly salaries paid per year as a
            :class:`TimeSeries` (typically ``14`` for Commercio).
        seniority_increments: Seniority increment rules.
    """

    hourly_divisor: int
    additional_months: TimeSeries
    seniority_increments: SeniorityIncrements


class Level(BaseModel):
    """A single classification level (*livello di inquadramento*).

    Attributes:
        code: Short identifier matching keys in
            :attr:`SeniorityIncrements.amount_by_level`
            (e.g. ``"4"``).
        order: Strict total ordering across levels — ``1`` is the lowest
            salary, ascending. Used by the cross-field validator to verify
            that salaries are non-decreasing by order at every date.
        description: Human-readable description.
        base_salary: Monthly base salary (*paga base tabellare*) as a
            :class:`TimeSeries`.
        fixed_allowances: Fixed monthly allowances attached to this level
            (e.g. contingenza, EDR, indennità funzione).
    """

    code: str
    order: int
    description: str
    base_salary: TimeSeries
    fixed_allowances: list[Allowance] = []

    @model_validator(mode="after")
    def _check_salary_non_decreasing(self) -> Self:
        """Validate that base_salary values do not decrease over time."""
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
    """Declares what is and is not implemented for a CCNL data file.

    Attributes:
        layer_1: Base salary and seniority computation status.
        layer_2: Employment type variations (part-time, fixed-term,
            apprenticeship) status.
        layer_3: Overtime, premiums, leave, sick pay status.
        notes: Free-text notes, especially for out-of-scope items.
    """

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
    """Identifying metadata for a CCNL.

    Attributes:
        id: Stable machine-readable identifier (e.g.
            ``"commercio-confcommercio"``).
        name: Full name of the contract.
        cnel_code: CNEL archive code (e.g. ``"H011"``).
        sector: Broad human-readable sector description (e.g.
            ``"terziario"``).
        tax_sector: INPS sector used to select the correct contribution-rate
            file (see :class:`TaxSector`).
        signatories: Employer and union associations that signed the CCNL.
        sources: Primary source references used to build the data file.
        extraction: Provenance metadata for the data file.
    """

    id: str
    name: str
    cnel_code: str
    sector: str
    tax_sector: TaxSector
    signatories: list[str]
    sources: list[CCNLSource]
    extraction: CCNLExtraction


class CCNL(BaseModel):
    """Root model for a CCNL data file.

    Cross-field invariants enforced at construction:

    1. Level ``order`` values are unique.
    2. Level ``code`` values are unique.
    3. Every key in
       :attr:`Parameters.seniority_increments.amount_by_level`
       corresponds to an existing level code.
    4. At every date where any level's base salary changes, the salary
       values are non-decreasing in level order (i.e., higher-order levels
       earn at least as much as lower-order levels).
    """

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
        """Validate cross-model invariants."""
        self._assert_unique_orders()
        self._assert_unique_codes()
        self._assert_seniority_level_codes()
        self._assert_salary_order_non_decreasing()
        return self

    # ------------------------------------------------------------------
    # Private helpers (called only from _validate_cross_fields)
    # ------------------------------------------------------------------

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
        """Verify salary non-decreasing by order at every transition date."""
        if len(self.levels) < 2:
            return
        sorted_levels = sorted(self.levels, key=lambda lv: lv.order)
        # Collect the union of all valid_from dates across all levels
        all_dates: set[date] = set()
        for lv in sorted_levels:
            for period in lv.base_salary.periods:
                all_dates.add(period.valid_from)
        # At each date, verify salary non-decreasing by ascending order
        for check_date in sorted(all_dates):
            prev_value: Decimal | None = None
            prev_code: str = ""
            for lv in sorted_levels:
                try:
                    value = lv.base_salary.value_at(check_date)
                except ValueError:
                    # Level series hasn't started yet at check_date; skip
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
