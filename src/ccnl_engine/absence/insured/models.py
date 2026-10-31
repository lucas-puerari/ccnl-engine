"""The indemnities of the absences an insurer pays, and the CCNL top-up.

During a maternity leave INPS pays 80% of the daily pay (D.Lgs. 151/2001
art. 22); after a work injury the employer pays the injury day and a
waiting period and INAIL pays from the fourth day (D.P.R. 1124/1965 artt.
68 and 73).  The statutory measures are :class:`InsuredAbsenceRates`, one
bundled table; what a CCNL adds is :class:`InsuredAbsenceRules`, in its
work rules.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.absence.insured.parental.models import ParentalRates
from ccnl_engine.provenance.ruleset.models import RulesetIdentity
from ccnl_engine.provenance.source.rule.models import RuleProvenance

__all__ = [
    "ExtraordinaryLeaveRates",
    "InjuryBand",
    "InjuryRates",
    "InjuryRules",
    "InsuredAbsenceRates",
    "InsuredAbsenceRules",
    "MaternityRates",
    "MaternityRules",
    "RestPermitRates",
    "YearCeiling",
]

#: A share of the pay, above zero and up to one.
type Share = Annotated[Decimal, Field(gt=Decimal(0), le=Decimal(1))]


class MaternityRates(BaseModel):
    """INPS maternity indemnity (D.Lgs. 151/2001 artt. 22-23).

    Attributes:
        indemnity_rate: Share of the daily pay INPS pays, 80%.
        daily_divisor: Days the pay of the month before is divided by, 30.
        provenance: Source of the measures.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    indemnity_rate: Share
    daily_divisor: int = Field(ge=1)
    provenance: RuleProvenance


class PaternityRates(BaseModel):
    """INPS indemnity of the compulsory paternity leave (D.Lgs. 151/2001).

    Attributes:
        indemnity_rate: Share of the daily pay INPS pays, 100% (art. 29).
        daily_divisor: Days the pay of the month before is divided by, 30
            (art. 23, which art. 29 applies).
        days: Working days of the leave, 10 (art. 27-bis c. 1).
        multiple_birth_days: Working days for a multiple birth, 20 (c. 2).
        provenance: Source of the measures.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    indemnity_rate: Share
    daily_divisor: int = Field(ge=1)
    days: int = Field(ge=1)
    multiple_birth_days: int = Field(ge=1)
    provenance: RuleProvenance


class RestPermitRates(BaseModel):
    """INPS indemnity of a rest or a permit of Capo V D.Lgs. 151/2001.

    Attributes:
        indemnity_rate: Share of the pay of the rest or permit INPS pays,
            100% (art. 43 c. 1, which art. 33 c. 4 L. 104/1992 applies to
            the permits to assist a disabled person).
        provenance: Source of the measure.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    indemnity_rate: Share
    provenance: RuleProvenance


class YearCeiling(BaseModel):
    """The most an indemnity pays a day in a year.

    Attributes:
        year: The calendar year.
        amount: The daily maximum.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    year: int
    amount: Decimal = Field(gt=Decimal(0))


class ExtraordinaryLeaveRates(BaseModel):
    """INPS indemnity of the extraordinary leave (art. 42 c. 5 D.Lgs. 151/2001).

    Attributes:
        daily_ceilings: The daily maximum of each year INPS published.
        provenance: Source of the measures.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    daily_ceilings: tuple[YearCeiling, ...]
    provenance: RuleProvenance

    def ceiling(self, year: int) -> Decimal | None:
        """Return the daily maximum of ``year``.

        Returns:
            The maximum, ``None`` for a year the bundle does not list.
        """
        return next((c.amount for c in self.daily_ceilings if c.year == year), None)


class InjuryBand(BaseModel):
    """An INAIL indemnity rate from a day of the inability.

    Attributes:
        day_from: Day counted from the injury day (the injury day is 0).
        rate: Share of the daily base INAIL pays from that day.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    day_from: int = Field(ge=1)
    rate: Share


class InjuryRates(BaseModel):
    """Statutory pay of a temporary inability after a work injury.

    Attributes:
        injury_day_rate: Share of the pay the employer pays for the injury
            day (art. 73: in full).
        carenza_days: Days after the injury day the employer pays (art. 73).
        carenza_rate: Share of the pay of each of those days (60%), unless
            the CCNL pays more.
        bands: INAIL rates from their first day, in day order.
        weekly_days: Days the weekly earnings are divided by for the daily
            base (art. 116 c. 2: the sixth part).
        provenance: Source of the measures.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    injury_day_rate: Share
    carenza_days: int = Field(ge=0)
    carenza_rate: Share
    bands: tuple[InjuryBand, ...] = Field(min_length=1)
    weekly_days: int = Field(ge=1)
    provenance: RuleProvenance

    @model_validator(mode="after")
    def _check_bands(self) -> Self:
        days = [b.day_from for b in self.bands]
        if days != sorted(set(days)) or days[0] != self.carenza_days + 1:
            msg = (
                "injury bands must start the day after the waiting period and "
                f"be in day order; got {days}"
            )
            raise ValueError(msg)
        return self

    def rate_on(self, day: int) -> Decimal:
        """Return the INAIL rate of day ``day`` after the injury day.

        Returns:
            The rate of the last band starting on or before ``day``.
        """
        return next(b.rate for b in reversed(self.bands) if b.day_from <= day)


class InsuredAbsenceRates(BaseModel):
    """The statutory indemnities of the bundle.

    Attributes:
        maternity: The INPS maternity indemnity.
        paternity: The INPS indemnity of the compulsory paternity leave.
        parental: The INPS indemnity of the parental leave.
        disability_permit: The INPS indemnity of the L. 104/1992 permits.
        nursing_rest: The INPS indemnity of the daily rests of the first
            year of a child (artt. 39-41).
        extraordinary_leave: The INPS indemnity of the extraordinary leave.
        injury: The pay of a temporary inability after a work injury.
        ruleset: Identity of the data file.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    maternity: MaternityRates
    paternity: PaternityRates
    parental: ParentalRates
    disability_permit: RestPermitRates
    nursing_rest: RestPermitRates
    extraordinary_leave: ExtraordinaryLeaveRates
    injury: InjuryRates
    ruleset: RulesetIdentity | None = None


class MaternityRules(BaseModel):
    """What a CCNL adds to the INPS maternity indemnity.

    Attributes:
        integration_rate: Share of the pay the employer tops the indemnity
            up to.
        integration_days: Days of the leave, from its first day, the
            top-up is due for (five months: 150).
        net_basis: Whether the measure is of the net pay (the INPS share,
            free of contributions, is grossed up by the worker's INPS rate).
        provenance: Source of the clause.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    integration_rate: Share
    integration_days: int = Field(ge=1)
    net_basis: bool
    provenance: RuleProvenance


class InjuryRules(BaseModel):
    """What a CCNL adds to the statutory pay of a work injury.

    Attributes:
        carenza_rate: Share of the pay the employer pays for the days of
            the waiting period, ``None`` for the statutory 60%.
        integration_rate: Share of the pay the employer tops the INAIL
            indemnity up to, ``None`` for no top-up.
        net_basis: Whether the measures are of the net pay.
        advanced: Whether the employer advances the INAIL indemnity on the
            payslip (and claims it back from INAIL).
        advanced_permanent_only: Whether it advances it to permanent
            workers only.
        provenance: Source of the clause.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    carenza_rate: Decimal | None = Field(default=None, gt=Decimal(0), le=Decimal(1))
    integration_rate: Decimal | None = Field(default=None, gt=Decimal(0), le=Decimal(1))
    net_basis: bool = False
    advanced: bool = False
    advanced_permanent_only: bool = False
    provenance: RuleProvenance


class InsuredAbsenceRules(BaseModel):
    """The CCNL treatment of the absences an insurer pays.

    Attributes:
        maternity: The top-up of the maternity indemnity, ``None`` when the
            CCNL adds nothing.
        injury: The treatment of a work injury, ``None`` when the CCNL adds
            nothing.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    maternity: MaternityRules | None = None
    injury: InjuryRules | None = None
