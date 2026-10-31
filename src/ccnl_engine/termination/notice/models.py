"""The notice a CCNL sets for the end of an open-ended employment.

Art. 2118 c.c. leaves the notice to the collective agreement: each band of
the CCNL names the levels it applies to, the longest service it covers,
the length of the notice and the indemnity owed in its place, in monthly
pays (mensilità).  The notice runs from the day after the act is received
when the CCNL says so.
"""

from __future__ import annotations

from decimal import Decimal
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.employment.period.inputs import TerminationCause
from ccnl_engine.provenance.source.rule.models import RuleProvenance

__all__ = ["NoticeBand", "NoticeRules", "NoticeStart"]


class NoticeStart(StrEnum):
    """The day the notice of a CCNL starts from.

    Attributes:
        DAY_AFTER: The day after the act is received.
        FIRST_OR_SIXTEENTH: The first 1st or 16th of a month after the act
            is received.
    """

    DAY_AFTER = "day_after"
    FIRST_OR_SIXTEENTH = "first_or_sixteenth"


class NoticeBand(BaseModel):
    """The notice of some levels up to a length of service.

    Attributes:
        levels: Level codes the band applies to.
        causes: The terminations the band applies to.
        up_to_months: Longest service in months the band covers,
            inclusive; ``None`` for any longer service.
        months: Calendar months of notice.
        days: Further days of notice.
        indemnity_months: Monthly pays owed for a notice not given;
            ``None`` when the CCNL measures the indemnity on the pay of the
            calendar days of notice.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    levels: tuple[str, ...] = Field(min_length=1)
    causes: tuple[TerminationCause, ...] = Field(min_length=1)
    up_to_months: int | None = Field(default=None, ge=1)
    months: int = Field(default=0, ge=0)
    days: int = Field(default=0, ge=0)
    indemnity_months: Decimal | None = Field(default=None, gt=Decimal(0))

    @model_validator(mode="after")
    def _has_length(self) -> Self:
        if not self.months and not self.days:
            msg = "a notice band needs months or days of notice"
            raise ValueError(msg)
        return self


class NoticeRules(BaseModel):
    """The notice of a CCNL, by level, cause and length of service.

    Attributes:
        bands: The bands; for a level and a cause, ordered by
            ``up_to_months`` with the open-ended band last.
        starts: The day the notice starts from.
        extra_months_included: Whether the indemnity carries the rateo of
            the extra monthly payments of the year.
        tfr_base: Whether the indemnity is in the TFR base by the CCNL;
            ``None`` when the CCNL does not say, and then it is out of it
            (Cass. 19 January 2023 n. 1581).
        provenance: Source of the clause.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    bands: tuple[NoticeBand, ...] = Field(min_length=1)
    starts: NoticeStart = NoticeStart.DAY_AFTER
    extra_months_included: bool = False
    tfr_base: bool | None = None
    provenance: RuleProvenance

    @model_validator(mode="after")
    def _ordered(self) -> Self:
        keys = {(lv, c) for b in self.bands for lv in b.levels for c in b.causes}
        for level, cause in sorted(keys):
            ceilings = [
                b.up_to_months
                for b in self.bands
                if level in b.levels and cause in b.causes
            ]
            bounded = [c for c in ceilings if c is not None]
            if (
                bounded != sorted(set(bounded))
                or ceilings[-1:] != [None]
                or (ceilings.count(None) != 1)
            ):
                msg = (
                    f"the notice bands of level {level} on {cause.value} must "
                    "grow in service, each ceiling once, the last open-ended"
                )
                raise ValueError(msg)
        return self

    def band(
        self, level: str, cause: TerminationCause, months_of_service: int
    ) -> NoticeBand | None:
        """Return the band of ``level`` and ``cause`` for a length of service.

        Returns:
            The first band whose ceiling the service does not exceed;
            ``None`` when the CCNL sets no notice for the level or cause.
        """
        return next(
            (
                b
                for b in self.bands
                if level in b.levels
                and cause in b.causes
                and (b.up_to_months is None or months_of_service <= b.up_to_months)
            ),
            None,
        )
