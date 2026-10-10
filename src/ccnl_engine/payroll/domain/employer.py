"""Employer domain types: headcount value object and employer profile."""

from __future__ import annotations

from dataclasses import dataclass

from ccnl_engine.shared.domain.validation import (
    parse_enum,
    require_bool,
    require_instance,
    require_int,
)
from ccnl_engine.tax.domain.preferential_regime import EmployerActivity

__all__ = ["EmployerActivity", "EmployerProfile", "Headcount"]

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
    classification of the employer follows from the CCNL, so the headcount
    is the only contribution fact the employer declares.

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
        provincial_pay_element: Whether a provincial pay element of the CCNL
            (a terzo elemento provinciale) is in force where the worker
            works, replacing the national element the CCNL pays only in its
            absence (Commercio Art. 215).  ``None`` means not known: a level
            with such a national element leaves it out and has a
            ``missing_fact`` blocker.

    Raises:
        InvalidInputError: When ``headcount`` is not a :class:`Headcount`,
            ``activity`` is not an :class:`EmployerActivity` value or
            ``public_life_insurance``, ``fis_reduction`` or
            ``provincial_pay_element`` is not a bool.
    """

    headcount: Headcount
    activity: EmployerActivity | None = None
    public_life_insurance: bool | None = None
    fis_reduction: bool | None = None
    provincial_pay_element: bool | None = None

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
        if self.public_life_insurance is not None:
            require_bool(
                self.public_life_insurance,
                "EmployerProfile.public_life_insurance",
                feature=_FEATURE,
            )
        for name in ("fis_reduction", "provincial_pay_element"):
            value = getattr(self, name)
            if value is not None:
                require_bool(value, f"EmployerProfile.{name}", feature=_FEATURE)
