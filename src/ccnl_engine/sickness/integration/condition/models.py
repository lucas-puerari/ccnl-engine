"""What a CCNL pays apart in a sick episode.

The short absences, the carenza by event, the hospital stays and the serious
illnesses.
"""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "CarenzaByEvent",
    "HospitalStayRule",
    "SeriousIllnessRule",
    "ShortAbsenceReduction",
]

_ONE = Decimal(1)


class ShortAbsenceReduction(BaseModel):
    """Lower pay of the first days of repeated short absences in a year.

    Attributes:
        max_days: Longest absence, in calendar days, that counts as short.
        from_event: First short absence of the calendar year reduced.
        first_days: Days of each reduced absence paid at the reduced rate.
        rates: Rate of the ``from_event``-th short absence, then of each
            later one; the last rate applies to every absence after it.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    max_days: int = Field(ge=1)
    from_event: int = Field(ge=2)
    first_days: int = Field(ge=1)
    rates: tuple[Decimal, ...] = Field(min_length=1)

    def rate_of(self, ordinal: int) -> Decimal:
        """Return the pay rate of the first days of the ``ordinal``-th absence.

        Returns:
            ``1`` before :attr:`from_event`, the matching rate after.
        """
        if ordinal < self.from_event:
            return _ONE
        return self.rates[min(ordinal - self.from_event, len(self.rates) - 1)]


class CarenzaByEvent(BaseModel):
    """Carenza paid at a lower rate from the n-th sickness event of a year.

    Commercio Art. 187: the carenza is integrated at 100% for the first two
    events of the calendar year, 66% for the third, 50% for the fourth and
    not from the fifth.  A relapse continues its event; an event the CCNL
    exempts (``SicknessEpisode.short_absence_exempt``) is not counted.

    Attributes:
        from_event: First event of the calendar year paid less.
        rates: Carenza rate of the ``from_event``-th event, then of each
            later one; the last rate applies to every event after it.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    from_event: int = Field(ge=2)
    rates: tuple[Decimal, ...] = Field(min_length=1)

    def rate_of(self, ordinal: int) -> Decimal:
        """Return the carenza rate of the ``ordinal``-th event of the year.

        Returns:
            ``1`` before :attr:`from_event`, the matching rate after.
        """
        if ordinal < self.from_event:
            return _ONE
        return self.rates[min(ordinal - self.from_event, len(self.rates) - 1)]


class HospitalStayRule(BaseModel):
    """Hospital stays paid in full within a reduced treatment.

    Federmeccanica Sez. Quarta Titolo VI art. 2: "I periodi di ricovero
    ospedaliero di durata superiore a 10 giorni continuativi sono retribuiti
    con l'intera retribuzione globale in aggiunta al trattamento economico
    di cui sopra fino ad un massimo di 61 giorni di calendario".

    Attributes:
        more_than_days: A stay counts when it lasts more than these
            consecutive days.
        max_full_days: Days of such stays paid in full at most, counted in
            the episode.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    more_than_days: int = Field(ge=0)
    max_full_days: int = Field(ge=1)


class SeriousIllnessRule(BaseModel):
    """Treatment of a particularly serious illness.

    Logistica Confetra art. 63: the "malattie particolarmente gravi, di cui
    alla circolare Inps 7.6.2016 n.95" are left out of the comporto count
    (c. 8) and paid "con la corresponsione dell'intera retribuzione globale
    mensile per 18 mesi" (c. 12).

    Concia art. 60 B instead extends the comporto of the "malattie
    invalidanti" (:attr:`SicknessSeniorityBand.serious_comporto_days`).

    Attributes:
        full_pay_days: Days of the episode paid in full; ``None`` when the
            CCNL pays it as any other.
        outside_comporto: Whether the episode is left out of the comporto.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    full_pay_days: int | None = Field(default=None, ge=1)
    outside_comporto: bool = False
