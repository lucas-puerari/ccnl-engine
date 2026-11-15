"""The rule of a CCNL on the parental leave by the hour.

Art. 32 c. 1-bis D.Lgs. 151/2001 leaves to collective bargaining the ways
of the leave by the hour, the hourly base and "l'equiparazione di un
determinato monte ore alla singola giornata lavorativa"; c. 1-ter applies
its general criterion (half the average daily hours a day, two such days a
day of leave, no cumulation with the other permits and rests of the
decree) "in assenza di una contrattazione collettiva che disciplini
compiutamente il congedo parentale su base oraria" (INPS circ. 152/2015
par. 2.1 and 2.2).  A CCNL that sets no hours to a day of leave leaves the
criterion in force.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.provenance.source.rule.models import RuleProvenance

__all__ = ["ParentalHourlyClause"]


class ParentalHourlyClause(BaseModel):
    """What a CCNL sets for the parental leave by the hour.

    Attributes:
        day_hours: Hours of a full-time worker that make one day of leave;
            ``None`` when the CCNL does not set them and the general
            criterion of art. 32 c. 1-ter applies.
        part_time_scaled: The CCNL scales ``day_hours`` by the part-time
            ratio.
        effective_from: First day the CCNL rule applies, ``None`` for every
            day of the CCNL; before it the general criterion applies.
        provenance: The CCNL clause, or the law and the CCNL text searched
            when the CCNL is silent.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    day_hours: Decimal | None = Field(default=None, gt=0)
    part_time_scaled: bool = False
    effective_from: date | None = None
    provenance: RuleProvenance

    def sets_hours_on(self, day: date) -> bool:
        """Return whether the CCNL's own hours to a day of leave apply on ``day``.

        Returns:
            ``True`` when the clause sets ``day_hours`` and is in force on
            ``day``; ``False`` when the general criterion applies.
        """
        if self.day_hours is None:
            return False
        return self.effective_from is None or day >= self.effective_from
