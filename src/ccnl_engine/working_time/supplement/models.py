"""The CCNL supplement bands of night, holiday and shift work and the hourly base."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from ccnl_engine.agreement.validity.rules import TimeSeries
from ccnl_engine.provenance.source.rule.models import RuleProvenance


class HourlyBaseMethod(StrEnum):
    """Monthly pay elements the CCNL divides by its hourly divisor.

    The individual elements of the worker (superminimi, aumenti di merito,
    assegni ad personam) enter it as :class:`IndividualElementsRule` says.

    Attributes:
        MINIMO_TABELLARE: The base salary of the level only.
        MINIMO_E_ANZIANITA: The base salary and the seniority increments,
            no allowance (CCNL chimica art. 15 punto 1 leaves the EDR out).
        GROSS_INCL_ALLOWANCES: The base salary, the seniority increments
            and every fixed allowance paid in cash.
    """

    MINIMO_TABELLARE = "minimo_tabellare"
    MINIMO_E_ANZIANITA = "minimo_e_anzianita"
    GROSS_INCL_ALLOWANCES = "gross_incl_allowances"


class IndividualInBase(StrEnum):
    """Where the individual elements of the worker enter the hourly base.

    Attributes:
        INCLUDED: In the hourly rate of the hour and of every supplement
            (Federmeccanica Sez. Quarta Titolo IV art. 3: "gli aumenti di
            merito nonché gli altri compensi eventualmente fissati a mese").
        EXCLUDED: In neither (the CCNL lists only collective elements).
        HOUR_ONLY: In the rate of the hour, not in the base of its
            maggiorazione (Commercio art. 149: the hour at the retribuzione
            di fatto of art. 208, the maggiorazione on the normale
            retribuzione of art. 206).
    """

    INCLUDED = "included"
    EXCLUDED = "excluded"
    HOUR_ONLY = "hour_only"


class IndividualElementsRule(BaseModel):
    """The CCNL rule on the individual elements in the hourly base.

    Attributes:
        in_hourly_base: Where the elements enter.
        provenance: Source of the rule; the engine reads it only when
            ``verified``.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    in_hourly_base: IndividualInBase
    provenance: RuleProvenance


class SupplementWork(StrEnum):
    """Ordinary work a CCNL pays a supplement on, apart from overtime.

    Attributes:
        NIGHT: Ordinary hours worked at night.
        HOLIDAY: Hours worked on a public holiday (festività).
        HOLIDAY_COMPENSATORY_REST: Hours worked on a public holiday or rest
            day with a compensatory rest day (metalmeccanici: festivo con
            riposo compensativo).
        SUNDAY: Ordinary hours worked on a Sunday by a worker whose weekly
            rest falls on another day.
        REST_DAY: Hours worked on the weekly rest day.
        DAY_SHIFT: Hours of a rotating day shift.
        NIGHT_SHIFT: Hours of a rotating night shift.
    """

    NIGHT = "night"
    HOLIDAY = "holiday"
    HOLIDAY_COMPENSATORY_REST = "holiday_compensatory_rest"
    SUNDAY = "sunday"
    REST_DAY = "rest_day"
    DAY_SHIFT = "day_shift"
    NIGHT_SHIFT = "night_shift"


class SupplementBand(BaseModel):
    """CCNL supplement on ordinary night, holiday, Sunday or shift hours.

    The supplement of ``hours`` is ``rate * hours * hourly base``: the
    maggiorazione only, eligible for the work-time substitute tax.

    Attributes:
        code: Identifier of the band, unique in the CCNL.
        description: What the band pays.
        work: The work it pays.
        rate: Share of the hourly base (``0.25`` for 25%).
        base: Monthly pay elements of its hourly base when the CCNL names
            others than those of :attr:`TimeSupplements.hourly_base_method`
            (Pubblici Esercizi art. 130: paga base and contingenza only);
            ``None`` for the hourly base of the CCNL.
        hours_paid_apart: ``True`` when the CCNL also pays the hours
            themselves on top of the monthly pay ("oltre alla normale
            retribuzione, quella per le ore"), ``False`` when the monthly pay
            covers them, ``None`` when the text does not settle it.  The
            engine posts the supplement only; the hours paid apart are
            ordinary pay it does not post.
        role: Role code the band is reserved to (``Employment.roles``);
            ``None`` for the workers holding none of the roles of the
            other bands of the same work.
        levels: Level codes the band is reserved to; empty for every level.
        provenance: Source of the band.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    description: str
    work: SupplementWork
    rate: TimeSeries
    base: HourlyBaseMethod | None = None
    hours_paid_apart: bool | None
    role: str | None = None
    levels: tuple[str, ...] = ()
    provenance: RuleProvenance
