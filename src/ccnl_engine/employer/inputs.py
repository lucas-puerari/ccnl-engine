"""Employer domain types: headcount value object and employer profile."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

from ccnl_engine.agreement.types import TaxSector
from ccnl_engine.compensation.second_level.inputs import (
    SecondLevelElement,
    check_second_level_elements,
)
from ccnl_engine.contribution.zone.models import AgriculturalZone
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.regime.models import EmployerActivity
from ccnl_engine.validators import (
    parse_enum,
    require_bool,
    require_instance,
    require_int,
    require_str,
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
        value: Number of employees, ``>= 1``. For the CIGO 50-person
            threshold art. 13(2) requires the previous calendar year's
            average (or the closing count of the first month for a new
            employer). The engine uses this supplied value directly; it
            does not derive or validate that statutory average.

    Raises:
        InvalidInputError: When ``value`` is not an int or is below 1.
    """

    value: int

    def __post_init__(self) -> None:  # noqa: D105
        require_int(self.value, "Headcount.value", feature=_FEATURE, minimum=1)


def _validate_patron_day(day: str | None) -> None:
    """Reject non-calendar dates and non-zero-padded local holiday codes.

    Raises:
        InvalidInputError: When the code is not a valid MM-DD date.
    """
    if day is None:
        return
    field = "EmployerProfile.patron_saint_day"
    require_str(day, field, feature=_FEATURE)
    valid = re.fullmatch(r"[0-9]{2}-[0-9]{2}", day) is not None
    if valid:
        try:
            date(2024, int(day[:2]), int(day[3:]))
        except ValueError:
            valid = False
    if not valid:
        msg = f"{field} must be a valid MM-DD; got {day!r}"
        raise InvalidInputError(msg, field=field, feature=_FEATURE)


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
            Construction and stone-working employers may also owe activity-
            dependent CIGO (D.Lgs. 148/2015 art. 13 c. 1), independently of
            their INPS sector. Artisan stone working only in a workshop
            structurally and organizationally separate from extraction is
            excluded by art. 10(o); choose the separate-workshop activity.
            Industrial stone working remains covered by art. 10(n). Only
            agreements covering these activities require this fact to
            determine their CIGO contribution.
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
        second_level_premium: Whether the employer has company or
            territorial bargaining with economic content (a premio per
            obiettivi, di risultato) that replaces the element the CCNL owes
            in its absence (Unionalimentari: elemento di garanzia
            retributiva; metalmeccanici: elemento perequativo).  ``None``
            means not known: a level with such an element leaves it out and
            has a ``missing_fact`` blocker.
        subsector: Sub-sector of the CCNL the employer belongs to, by the
            code its time-supplement bands name (Alimentari art. 31:
            ``"vini_liquori"``, ``"conserve_vegetali"``...).  ``None`` means
            not known: on a CCNL whose bands differ by sub-sector the
            overtime is priced with its first table and the run has a
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
        sickness_window_counting: Whether the employer counts the comporto
            over the window its CCNL offers as an alternative (ABI Art. 66
            c. 2: the 48 months before the last day of absence) instead of
            each illness; raises on a CCNL that offers none.
        contractual_funds: Codes of the health and bilateral funds of the
            CCNL the employer pays (``parameters.health_funds``, e.g.
            ``"fondo_est"``); a fund of the CCNL not named owes the worker its
            elemento distinto instead.  ``None`` means not known: a run on a
            CCNL with such funds posts neither and has a ``missing_fact``
            blocker; an empty set states that the employer pays none.
        patron_saint_day: Local patron saint holiday as ``MM-DD``. ``None``
            means not stated; a clause that covers it then does not apply
            to that day.
        legacy_section_applicable: Whether the employer belongs to a legacy
            section of the CCNL carried forward from a previous agreement.
            ``None`` means unknown; a rule restricted to that section is
            withheld with a ``missing_fact`` blocker.
        permit_carryover: How the employer settles the permits not taken
            within their year, on a CCNL that leaves the choice
            (``LeaveRules.permit_deadline``, Commercio Art. 158): ``True``
            carries them to the deadline of the next year, ``False`` pays
            them with the December pay.  ``None`` means not known: the runs
            of December and of the deadline pay nothing and have a
            ``missing_fact`` blocker.

    Raises:
        InvalidInputError: When ``headcount`` is not a :class:`Headcount`,
            ``activity`` is not an :class:`EmployerActivity` value,
            ``agricultural_zone`` not an :class:`AgriculturalZone` value,
            ``inps_sector`` not a :class:`TaxSector` value or
            ``public_life_insurance``, ``fis_reduction``,
            ``provincial_pay_element``, ``second_level_premium``,
            ``permit_carryover``, ``legacy_section_applicable`` or
            ``sickness_window_counting`` is not a bool, or ``subsector`` is
            not a non-blank string.
    """

    headcount: Headcount
    activity: EmployerActivity | None = None
    public_life_insurance: bool | None = None
    fis_reduction: bool | None = None
    cigs_indotto: bool | None = None
    provincial_pay_element: bool | None = None
    second_level_premium: bool | None = None
    subsector: str | None = None
    agricultural_zone: AgriculturalZone | None = None
    inps_sector: TaxSector | None = None
    contractual_funds: frozenset[str] | None = None
    sickness_window_counting: bool = False
    permit_carryover: bool | None = None
    patron_saint_day: str | None = None
    legacy_section_applicable: bool | None = None
    second_level_elements: tuple[SecondLevelElement, ...] = ()

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
        if self.contractual_funds is not None:
            funds = self.contractual_funds
            if not isinstance(funds, (set, frozenset)) or not all(
                isinstance(code, str) for code in funds
            ):
                msg = (
                    "EmployerProfile.contractual_funds must be a set of fund codes"
                    f" (an empty set for none); got {funds!r}"
                )
                raise InvalidInputError(
                    msg, field="EmployerProfile.contractual_funds", feature=_FEATURE
                )
            object.__setattr__(self, "contractual_funds", frozenset(funds))
        object.__setattr__(
            self,
            "second_level_elements",
            check_second_level_elements(
                self.second_level_elements, "EmployerProfile.second_level_elements"
            ),
        )
        _validate_patron_day(self.patron_saint_day)
        require_str(
            self.subsector,
            "EmployerProfile.subsector",
            feature=_FEATURE,
            non_blank=True,
            optional=True,
        )
        for name in (
            "fis_reduction",
            "provincial_pay_element",
            "second_level_premium",
            "cigs_indotto",
            "sickness_window_counting",
            "permit_carryover",
            "legacy_section_applicable",
        ):
            value = getattr(self, name)
            if value is not None:
                require_bool(value, f"EmployerProfile.{name}", feature=_FEATURE)
