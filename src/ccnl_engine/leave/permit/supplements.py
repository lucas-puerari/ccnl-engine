"""Dated additions to annual permit hours by employer sector and worker shift."""

from __future__ import annotations

from datetime import date  # noqa: TC003
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.provenance.source.rule.models import RuleProvenance  # noqa: TC001

__all__ = ["PermitExtraHours"]


class PermitExtraHours(BaseModel):
    """Additional annual hours, additive to the base permit entitlement.

    ``subsectors`` restricts the hours to employer sub-sectors; an empty
    tuple covers all. ``excluded_subsectors`` removes the named sectors;
    if the employer sub-sector is unknown, this supplement cannot be granted.
    ``qualifying_shifts`` requires the worker's rotating shift pattern to
    include at least 15 weekly shifts with night and/or weekend shifts;
    ``min_weekly_shifts`` at least that many weekly shifts with the night
    shift (Federmeccanica art. 5: 18 from 2027, 21 from 2028).
    Dates bound the competence month, with an exclusive end.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    hours: Decimal = Field(gt=Decimal(0))
    valid_from: date | None = None
    valid_until: date | None = None
    subsectors: tuple[str, ...] = ()
    excluded_subsectors: tuple[str, ...] = ()
    qualifying_shifts: bool = False
    min_weekly_shifts: int | None = Field(default=None, gt=0)
    provenance: RuleProvenance

    def _active(self, day: date, subsector: str | None) -> bool:
        """Return whether the date and any required sector allow the hours.

        Returns:
            ``True`` when the date and inclusive sector match.
        """
        return (
            (self.valid_from is None or day >= self.valid_from)
            and (self.valid_until is None or day < self.valid_until)
            and (not self.subsectors or subsector in self.subsectors)
        )

    def shift_fact_unknown(
        self,
        day: date,
        subsector: str | None,
        shifts: bool | None,
        weekly: int | None = None,
    ) -> bool:
        """Return whether missing shift or sector facts could change the credit.

        Returns:
            ``True`` when a payable shift supplement cannot be resolved.
        """
        if self.min_weekly_shifts is not None:
            return (
                self._active(day, subsector)
                and subsector not in self.excluded_subsectors
                and weekly is None
                and shifts is not False
            )
        return (
            self.qualifying_shifts
            and self._active(day, subsector)
            and subsector not in self.excluded_subsectors
            and (
                shifts is None
                or (
                    shifts is True
                    and subsector is None
                    and bool(self.excluded_subsectors)
                )
            )
        )

    def applies(
        self,
        day: date,
        subsector: str | None,
        shifts: bool | None,
        weekly: int | None = None,
    ) -> bool:
        """Return whether this supplement is due for these facts.

        Returns:
            ``True`` when the date, sub-sector and shift match.
        """
        return (
            self._active(day, subsector)
            and (
                not self.excluded_subsectors
                or (subsector is not None and subsector not in self.excluded_subsectors)
            )
            and (not self.qualifying_shifts or shifts is True)
            and (
                self.min_weekly_shifts is None
                or (weekly is not None and weekly >= self.min_weekly_shifts)
            )
        )
