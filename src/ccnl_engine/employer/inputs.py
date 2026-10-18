"""Employer domain types: headcount value object and employer profile."""

from __future__ import annotations

from dataclasses import dataclass

from ccnl_engine.agreement.types import TaxSector
from ccnl_engine.contribution.zone.models import AgriculturalZone
from ccnl_engine.regime.models import EmployerActivity
from ccnl_engine.validators import (
    parse_enum,
    require_bool,
    require_instance,
    require_int,
)

__all__ = [
    "AgriculturalZone",
    "EmployerActivity",
    "EmployerProfile",
    "Headcount",
    "TaxSector",
]

_FEATURE = "employer"


@dataclass(frozen=True, slots=True)
class Headcount:
    """Employer headcount used to select INPS contribution tiers.

    At least one: the worker being paid is an employee of the employer.

    Attributes:
        value: Number of employees, ``>= 1``.

    Raises:
        InvalidInputError: When ``value`` is not an int or is below 1.
    """

    value: int

    def __post_init__(self) -> None:  # noqa: D105
        require_int(self.value, "Headcount.value", feature=_FEATURE, minimum=1)


@dataclass(frozen=True, slots=True)
class EmployerProfile:
    """The employer of the worker being paid.

    The only employer model of the payroll pipeline.  The INPS
    classification of the employer follows from the CCNL, unless the CCNL
    is applied by employers of more than one INPS sector: then the
    employer states its sector.

    Attributes:
        headcount: Employer headcount, used to select the INPS contribution
            tier.  Required: no size is assumed.
        activity: Activity of the employer, for the regimes that exclude
            some activities.  ``None`` means not known: the night, holiday
            and shift substitute tax (L. 199/2025 art. 1 c. 11) excludes the
            activities of c. 18, so its eligibility is then ``unknown``.
        public_life_insurance: Whether a public employer enrols its staff in
            the Assicurazione Sociale Vita (ex ENPDEP): every "ente dotato di
            personalità giuridica di diritto pubblico" except the State, the
            Province, the Comuni and the enti di assistenza e beneficenza
            (INPS circ. 104/2014).  ``None`` takes the value the CCNL fixes;
            when it fixes none, a run of the public administrations has a
            ``missing_fact`` blocker.
        fis_reduction: Whether an employer of the fondo di integrazione
            salariale with on average up to five employees has its rate cut
            by 40% for not having applied for the assegno di integrazione
            salariale in the last twenty-four months (D.Lgs. 148/2015 art. 29
            c. 8-bis).  ``None`` means not known: a run of such an employer
            has a ``missing_fact`` blocker and is charged the full rate.
        cigs_indotto: Whether a craft firm with more than fifteen employees
            works in the indotto of a firm with the prevailing management
            influence, owing the CIGS contribution (D.Lgs. 148/2015 art. 20
            c. 1 lett. b, art. 23 c. 1).  ``None`` means not known: a run of
            such an employer has a ``missing_fact`` issue and is charged
            without it.
        provincial_pay_element: Whether a provincial pay element of the CCNL
            (a terzo elemento provinciale) is in force where the worker
            works, replacing the national element the CCNL pays only in its
            absence (Commercio Art. 215).  ``None`` means not known: a level
            with such a national element leaves it out and has a
            ``missing_fact`` blocker.
        agricultural_zone: Zone of the land of an agricultural employer,
            which cuts its INPS contributions by 68% in a zona svantaggiata
            and 75% in a zona particolarmente svantaggiata (INPS circ.
            43/2026 par. 7).  ``None`` means not known: an agricultural run
            is charged the full rates and has a ``missing_fact`` blocker.
        inps_sector: INPS sector of the classification of the employer (art.
            49 L. 88/1989), by the activity it carries out: a CCNL applied
            by employers of more than one sector (Logistica: an autotrasporto
            firm is industria, a spedizioniere terziario) lists them in
            ``CCNLMeta.inps_sectors``.  ``None`` takes the sector of the
            CCNL; when it lists more than one, the run has a
            ``missing_fact`` blocker.  A sector the CCNL does not list
            raises.

    Raises:
        InvalidInputError: When ``headcount`` is not a :class:`Headcount`,
            ``activity`` is not an :class:`EmployerActivity` value,
            ``agricultural_zone`` not an :class:`AgriculturalZone` value,
            ``inps_sector`` not a :class:`TaxSector` value or
            ``public_life_insurance``, ``fis_reduction`` or
            ``provincial_pay_element`` is not a bool.
    """

    headcount: Headcount
    activity: EmployerActivity | None = None
    public_life_insurance: bool | None = None
    fis_reduction: bool | None = None
    cigs_indotto: bool | None = None
    provincial_pay_element: bool | None = None
    agricultural_zone: AgriculturalZone | None = None
    inps_sector: TaxSector | None = None

    def __post_init__(self) -> None:  # noqa: D105
        require_instance(
            self.headcount, Headcount, "EmployerProfile.headcount", feature=_FEATURE
        )
        if self.activity is not None:
            activity = parse_enum(
                self.activity,
                EmployerActivity,
                "EmployerProfile.activity",
                feature=_FEATURE,
            )
            object.__setattr__(self, "activity", activity)
        if self.agricultural_zone is not None:
            zone = parse_enum(
                self.agricultural_zone,
                AgriculturalZone,
                "EmployerProfile.agricultural_zone",
                feature=_FEATURE,
            )
            object.__setattr__(self, "agricultural_zone", zone)
        if self.inps_sector is not None:
            sector = parse_enum(
                self.inps_sector,
                TaxSector,
                "EmployerProfile.inps_sector",
                feature=_FEATURE,
            )
            object.__setattr__(self, "inps_sector", sector)
        if self.public_life_insurance is not None:
            require_bool(
                self.public_life_insurance,
                "EmployerProfile.public_life_insurance",
                feature=_FEATURE,
            )
        for name in ("fis_reduction", "provincial_pay_element", "cigs_indotto"):
            value = getattr(self, name)
            if value is not None:
                require_bool(value, f"EmployerProfile.{name}", feature=_FEATURE)
