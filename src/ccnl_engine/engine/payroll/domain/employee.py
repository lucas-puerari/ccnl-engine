"""Worker-side domain types: seniority, RAL overrides, Jurisdiction, Employee."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.engine.contract.domain.ccnl import LevelCategory
from ccnl_engine.engine.primitives.domain.primitives import StrictDecimal

_ZERO: Decimal = Decimal(0)
_ONE: Decimal = Decimal(1)


# ---------------------------------------------------------------------------
# Seniority discriminated union
# ---------------------------------------------------------------------------


class SeniorityByCount(BaseModel):
    """Seniority expressed as an explicit number of *scatti* already accrued.

    Use this when you know the exact increment count. Mutually exclusive with
    :class:`SeniorityByMonths` — the union makes it impossible to supply both.

    Attributes:
        value: Number of seniority increments accrued. Must be ``>= 0``.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    type: Literal["count"] = "count"
    value: int = Field(ge=0)


class SeniorityByMonths(BaseModel):
    """Seniority expressed as months of service elapsed.

    The engine derives the increment count from the CCNL cadence rules.
    Use this when you track tenure in months rather than counting *scatti*
    manually. Mutually exclusive with :class:`SeniorityByCount`.

    Attributes:
        value: Months of continuous service elapsed. Must be ``>= 0``.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    type: Literal["months"] = "months"
    value: int = Field(ge=0)


class SeniorityByDate(BaseModel):
    """Seniority expressed as a hire or service-start date.

    The engine derives months of service from the gap between this date and
    :attr:`~ccnl_engine.engine.payroll.domain.scenario.Employment.as_of`,
    then applies the CCNL cadence rules to arrive at an increment count.

    Use this when you track the worker's hire date rather than months or
    increment count directly.

    Attributes:
        value: Hire date or continuous-service start date.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    type: Literal["date"] = "date"
    value: date


#: Union of all seniority input strategies.
Seniority = SeniorityByCount | SeniorityByMonths | SeniorityByDate


# ---------------------------------------------------------------------------
# RAL-override discriminated union
# ---------------------------------------------------------------------------


class RalOverride(BaseModel):
    """Replace the CCNL-derived gross annual salary with a fixed agreed value.

    Valid for any employment type. The value is used as-is (not scaled by
    the part-time coefficient). Mutually exclusive with
    :class:`DestinationRalOverride`.

    Attributes:
        value: Agreed annual salary in euros. Must be ``> 0``.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    type: Literal["ral"] = "ral"
    value: StrictDecimal

    @model_validator(mode="after")
    def _check_positive(self) -> RalOverride:
        if self.value <= _ZERO:
            msg = f"RalOverride.value must be > 0, got {self.value}"
            raise ValueError(msg)
        return self


class DestinationRalOverride(BaseModel):
    """Destination-level RAL for a percentage-track apprentice.

    The engine applies the apprenticeship percentage to this value to produce
    the apprentice's actual pay. Only valid for
    :class:`~ccnl_engine.engine.payroll.domain.employment.Apprentice`
    employment on a percentage track. Mutually exclusive with
    :class:`RalOverride`.

    Attributes:
        value: Destination-level annual salary in euros. Must be ``> 0``.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    type: Literal["destination_ral"] = "destination_ral"
    value: StrictDecimal

    @model_validator(mode="after")
    def _check_positive(self) -> DestinationRalOverride:
        if self.value <= _ZERO:
            msg = f"DestinationRalOverride.value must be > 0, got {self.value}"
            raise ValueError(msg)
        return self


#: Union of the two RAL-override strategies.
RalOverrideMode = RalOverride | DestinationRalOverride


# ---------------------------------------------------------------------------
# Jurisdiction
# ---------------------------------------------------------------------------


class Jurisdiction(BaseModel):
    """Fiscal residency of the worker.

    Used to compute addizionale regionale and addizionale comunale IRPEF.
    Both fields are optional: when both are ``None``, no surtax is loaded.

    Attributes:
        regione: Italian region name (e.g. ``"Lombardia"``).
        comune_belfiore: Codice catastale of the worker's municipality of
            residence (e.g. ``"F205"`` for Milan).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    regione: str | None = None
    comune_belfiore: str | None = None


# ---------------------------------------------------------------------------
# Agreement
# ---------------------------------------------------------------------------


class Agreement(BaseModel):
    """Individual salary terms that override the CCNL tables.

    Attributes:
        ral_override: When set, replaces the CCNL-derived gross annual
            salary. Use :class:`RalOverride` for any employment type, or
            :class:`DestinationRalOverride` for a percentage-track apprentice.
        ad_personam_monthly: Individual frozen monthly supplement added
            directly to gross (e.g. a pre-abolition seniority increment).
            Not scaled by ``part_time_ratio``. Must be ``>= 0``.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    ral_override: (
        Annotated[
            RalOverride | DestinationRalOverride,
            Field(discriminator="type"),
        ]
        | None
    ) = None
    ad_personam_monthly: StrictDecimal = _ZERO

    @model_validator(mode="after")
    def _check_non_negative(self) -> Agreement:
        if self.ad_personam_monthly < _ZERO:
            msg = f"ad_personam_monthly must be >= 0, got {self.ad_personam_monthly}"
            raise ValueError(msg)
        return self


# ---------------------------------------------------------------------------
# Employee
# ---------------------------------------------------------------------------


class Employee(BaseModel):
    """Worker-side inputs for payroll computation.

    Encodes who the worker is: their CCNL classification level, seniority,
    working-time arrangement, fiscal residency, and any individually agreed
    salary terms.

    Attributes:
        level_code: Classification level code as defined in the CCNL
            (e.g. ``"D3"``). Must match a level in the applied CCNL.
        seniority: Seniority expressed as an explicit increment count
            (:class:`SeniorityByCount`), as months of service
            (:class:`SeniorityByMonths`), or as a hire date
            (:class:`SeniorityByDate`). ``None`` means no increment applies.
        part_time_ratio: Part-time coefficient in the range ``(0, 1]``.
            Full-time workers use the default ``1``.
        weekly_hours: Contractual weekly hours. Required when the tax-rules
            file uses ``domestic_contributions`` (lavoro domestico).
            Must be ``> 0`` when provided.
        category: Worker category override (``"operaio"``, ``"impiegato"``,
            etc.). Required when a level hosts multiple categories.
            Defaults to the level's own category when ``None``.
        roles: Set of role identifiers the worker holds (e.g.
            ``{"capoturno"}``). Selects role-restricted allowances.
        ivs_ceiling_applies: Set to ``True`` when the worker's gross is
            above the INPS IVS ceiling and only the IVS-specific
            contribution rate should apply.
        jurisdiction: Fiscal residency for addizionale regionale/comunale
            computation. ``None`` means no surtax is computed.
        agreement: Individual salary terms overriding the CCNL tables.
            ``None`` means the CCNL tables are used unchanged.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    level_code: str
    seniority: (
        Annotated[
            SeniorityByCount | SeniorityByMonths | SeniorityByDate,
            Field(discriminator="type"),
        ]
        | None
    ) = None
    part_time_ratio: StrictDecimal = _ONE
    weekly_hours: StrictDecimal | None = None
    category: LevelCategory | None = None
    roles: frozenset[str] = frozenset()
    ivs_ceiling_applies: bool = False
    jurisdiction: Jurisdiction | None = None
    agreement: Agreement | None = None

    @model_validator(mode="after")
    def _check_ranges(self) -> Employee:
        if not (_ZERO < self.part_time_ratio <= _ONE):
            msg = f"part_time_ratio must be in (0, 1], got {self.part_time_ratio}"
            raise ValueError(msg)
        if self.weekly_hours is not None and self.weekly_hours <= _ZERO:
            msg = f"weekly_hours must be > 0, got {self.weekly_hours}"
            raise ValueError(msg)
        return self

    @property
    def seniority_count(self) -> int | None:
        """Explicit increment count, or ``None`` when expressed as months."""
        return (
            self.seniority.value
            if isinstance(self.seniority, SeniorityByCount)
            else None
        )

    @property
    def seniority_months(self) -> int | None:
        """Service months elapsed, or ``None`` when expressed as a count or date.

        For date-based seniority, use :meth:`seniority_months_as_of` instead.
        """
        return (
            self.seniority.value
            if isinstance(self.seniority, SeniorityByMonths)
            else None
        )

    def seniority_months_as_of(self, as_of: date) -> int | None:
        """Return service months elapsed at *as_of*, resolving all variants.

        - :class:`SeniorityByMonths`: returns the stored months value directly.
        - :class:`SeniorityByDate`: computes the calendar-month gap between
          the hire date and *as_of*.
        - :class:`SeniorityByCount` or ``None``: returns ``None``.

        Args:
            as_of: The reference date, typically
                :attr:`~ccnl_engine.engine.payroll.domain.scenario\
.Employment.as_of`.

        Returns:
            Months of service, or ``None`` when seniority is expressed as
            a count or not provided.

        Raises:
            ValueError: If hire_date is after *as_of* (future employee).
        """
        if isinstance(self.seniority, SeniorityByMonths):
            return self.seniority.value
        if isinstance(self.seniority, SeniorityByDate):
            hire = self.seniority.value
            if hire > as_of:
                msg = (
                    f"hire_date {hire} is after as_of {as_of}: "
                    "cannot compute seniority for a future employee"
                )
                raise ValueError(msg)
            return (as_of.year - hire.year) * 12 + (as_of.month - hire.month)
        return None
