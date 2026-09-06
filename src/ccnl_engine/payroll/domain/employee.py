"""Employee and employer input models for :func:`~ccnl_engine.engine.compute.compute`.

The flat :class:`Scenario` has been replaced by a hierarchy of focused objects:

- :class:`Employee` — all worker-side inputs, composed of four sub-objects
- :class:`Employer` — employer-side inputs (second-level bargaining allowances)

Seniority and RAL-override inputs are expressed as discriminated unions so that
mutually-exclusive alternatives become structurally impossible to combine.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.contract.domain.ccnl import LevelCategory
    from ccnl_engine.payroll.domain.employment import Employment

_ZERO: Decimal = Decimal(0)
_ONE: Decimal = Decimal(1)


# ---------------------------------------------------------------------------
# Seniority discriminated union
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SeniorityByCount:
    """Seniority expressed as an explicit number of *scatti* already accrued.

    Use this when you know the exact increment count.  Mutually exclusive with
    :class:`SeniorityByMonths` — the union makes it impossible to supply both.

    Attributes:
        value: Number of seniority increments accrued.  Must be ``>= 0``.
    """

    value: int

    def __post_init__(self) -> None:
        """Validate that value is non-negative.

        Raises:
            ValueError: If value is negative.
        """
        if self.value < 0:
            msg = f"SeniorityByCount.value must be >= 0, got {self.value}"
            raise ValueError(msg)


@dataclass(frozen=True)
class SeniorityByMonths:
    """Seniority expressed as months of service elapsed.

    The engine derives the increment count from the CCNL cadence rules.
    Use this when you track tenure in months rather than counting *scatti*
    manually.  Mutually exclusive with :class:`SeniorityByCount`.

    Attributes:
        value: Months of continuous service elapsed.  Must be ``>= 0``.
    """

    value: int

    def __post_init__(self) -> None:
        """Validate that value is non-negative.

        Raises:
            ValueError: If value is negative.
        """
        if self.value < 0:
            msg = f"SeniorityByMonths.value must be >= 0, got {self.value}"
            raise ValueError(msg)


#: Union of the two seniority input strategies.
Seniority = SeniorityByCount | SeniorityByMonths


# ---------------------------------------------------------------------------
# RAL-override discriminated union
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RalOverride:
    """Replace the CCNL-derived gross annual salary with a fixed agreed value.

    Valid for any employment type.  The value is used as-is (not scaled by
    part-time coefficient).  Mutually exclusive with
    :class:`DestinationRalOverride`.

    Attributes:
        value: Agreed annual salary in euros.  Must be ``> 0``.
    """

    value: Decimal

    def __post_init__(self) -> None:
        """Validate that value is positive.

        Raises:
            ValueError: If value is zero or negative.
        """
        if self.value <= _ZERO:
            msg = f"RalOverride.value must be > 0, got {self.value}"
            raise ValueError(msg)


@dataclass(frozen=True)
class DestinationRalOverride:
    """Destination-level RAL for a percentage-track apprentice.

    The engine applies the apprenticeship percentage to this value to produce
    the apprentice's actual pay.  Only valid for :class:`~ccnl_engine.domain.\
employment.Apprentice` employment on a percentage track.  Mutually exclusive
    with :class:`RalOverride`.

    Attributes:
        value: Destination-level annual salary in euros.  Must be ``> 0``.
    """

    value: Decimal

    def __post_init__(self) -> None:
        """Validate that value is positive.

        Raises:
            ValueError: If value is zero or negative.
        """
        if self.value <= _ZERO:
            msg = f"DestinationRalOverride.value must be > 0, got {self.value}"
            raise ValueError(msg)


#: Union of the two RAL-override strategies.
RalOverrideMode = RalOverride | DestinationRalOverride


# ---------------------------------------------------------------------------
# Sub-objects
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ContractPosition:
    """The worker's position within the CCNL classification grid.

    Attributes:
        level_code: Classification level code as defined in the CCNL
            (e.g. ``"D3"``).  Must match a level in the provided CCNL.
        as_of: Reference date for all time-series lookups (base pay,
            seniority amounts, allowances).
        employment: Contract type — :class:`~ccnl_engine.domain.employment.\
Permanent`, :class:`~ccnl_engine.domain.employment.FixedTerm`, or
            :class:`~ccnl_engine.domain.employment.Apprentice`.
        category: Worker category override (``"operaio"``, ``"impiegato"``,
            ``"quadro"``, ``"dirigente"``).  Required when a level hosts
            multiple categories (e.g. edilizia level 3).  Defaults to the
            level's own category when ``None``.
        roles: Set of role identifiers the worker holds (e.g.
            ``{"capoturno"}``).  Selects role-restricted allowances defined
            in the CCNL level.
    """

    level_code: str
    as_of: date
    employment: Employment
    category: LevelCategory | None = None
    roles: frozenset[str] = frozenset()


@dataclass(frozen=True)
class WorkArrangement:
    """How the worker's hours and seniority are structured.

    Attributes:
        part_time_pct: Part-time coefficient in the range ``(0, 1]``.  A
            full-time worker uses the default ``1``.  Gross pay, INPS, and
            TFR are all scaled by this value.
        seniority: Seniority expressed either as a count of accrued
            increments (:class:`SeniorityByCount`) or as months of service
            (:class:`SeniorityByMonths`).  ``None`` means no increment
            applies.
        weekly_hours: Contractual weekly hours.  Required when the tax-rules
            file uses ``domestic_contributions`` (lavoro domestico).  Must
            be ``> 0`` when provided.
    """

    part_time_pct: Decimal = _ONE
    seniority: SeniorityByCount | SeniorityByMonths | None = None
    weekly_hours: Decimal | None = None

    def __post_init__(self) -> None:
        """Validate part_time_pct and weekly_hours ranges.

        Raises:
            ValueError: If part_time_pct is not in (0, 1] or weekly_hours <= 0.
        """
        if not (_ZERO < self.part_time_pct <= _ONE):
            msg = f"part_time_pct must be in (0, 1], got {self.part_time_pct}"
            raise ValueError(msg)
        if self.weekly_hours is not None and self.weekly_hours <= _ZERO:
            msg = f"weekly_hours must be > 0, got {self.weekly_hours}"
            raise ValueError(msg)

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
        """Service months elapsed, or ``None`` when expressed as a count."""
        return (
            self.seniority.value
            if isinstance(self.seniority, SeniorityByMonths)
            else None
        )


@dataclass(frozen=True)
class TaxProfile:
    """Tax-locality and contribution-ceiling settings for the worker.

    All fields are optional: omit the entire object (pass ``None`` for
    :attr:`Employee.tax`) when addizionali and IVS-ceiling logic are not
    needed.

    Attributes:
        regione: Italian region name for addizionale regionale IRPEF lookup
            (e.g. ``"Lombardia"``).  Ignored when no
            :class:`~ccnl_engine.surtax.models.SurtaxRules` is passed to
            :func:`~ccnl_engine.engine.compute.compute`.
        comune_belfiore: Codice catastale (Belfiore code) of the worker's
            municipality of residence (e.g. ``"H501"`` for Rome).  Ignored
            when no :class:`~ccnl_engine.surtax.models.SurtaxRules` is
            passed to :func:`~ccnl_engine.engine.compute.compute`.
        ivs_ceiling_applies: Set to ``True`` when the worker's gross is
            above the IVS ceiling and only the IVS-specific contribution
            rate should apply.  Defaults to ``False``.
    """

    regione: str | None = None
    comune_belfiore: str | None = None
    ivs_ceiling_applies: bool = False


@dataclass(frozen=True)
class SalaryOverrides:
    """Individually negotiated salary terms that override the CCNL tables.

    Attributes:
        ral_override: When set, replaces the CCNL-derived gross annual
            salary.  Use :class:`RalOverride` for any employment type, or
            :class:`DestinationRalOverride` for a percentage-track
            apprentice.  ``None`` means the CCNL tables are used unchanged.
        ad_personam_monthly: Individual frozen monthly element added
            directly to gross (e.g. a pre-abolition seniority increment).
            Not scaled by ``part_time_pct``.  Must be ``>= 0``.
    """

    ral_override: RalOverride | DestinationRalOverride | None = None
    ad_personam_monthly: Decimal = _ZERO

    def __post_init__(self) -> None:
        """Validate that ad_personam_monthly is non-negative.

        Raises:
            ValueError: If ad_personam_monthly is negative.
        """
        if self.ad_personam_monthly < _ZERO:
            msg = f"ad_personam_monthly must be >= 0, got {self.ad_personam_monthly}"
            raise ValueError(msg)


# ---------------------------------------------------------------------------
# Top-level objects
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Employee:
    """Worker-side inputs for :func:`~ccnl_engine.engine.compute.compute`.

    Replaces the flat ``Scenario`` with four semantically distinct sub-objects
    so that each field's purpose is unambiguous from its type alone.

    Attributes:
        position: Contract position within the CCNL classification grid.
        arrangement: Working-time and seniority settings.
        tax: Tax-locality and IVS-ceiling settings.  Pass ``None`` (the
            default) when addizionali and ceiling logic are not needed.
        agreement: Individually negotiated salary terms.  Pass ``None`` (the
            default) when no overrides apply.
    """

    position: ContractPosition
    arrangement: WorkArrangement
    tax: TaxProfile | None = None
    agreement: SalaryOverrides | None = None
