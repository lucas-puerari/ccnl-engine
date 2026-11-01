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

from ccnl_engine.employment.category.models import WorkerCategory
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
        categories: The worker categories the band applies to; empty for
            every category (Alimentari art. 72 sets apart impiegati,
            intermedi and operai of the same level).
        starts: The day the notice of the band starts from, when it is not
            the one of the CCNL (Alimentari: the operai from any day).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    levels: tuple[str, ...] = Field(min_length=1)
    causes: tuple[TerminationCause, ...] = Field(min_length=1)
    up_to_months: int | None = Field(default=None, ge=1)
    months: int = Field(default=0, ge=0)
    days: int = Field(default=0, ge=0)
    indemnity_months: Decimal | None = Field(default=None, gt=Decimal(0))
    categories: tuple[WorkerCategory, ...] = ()
    starts: NoticeStart | None = None

    def applies(
        self, level: str, cause: TerminationCause, category: WorkerCategory | None
    ) -> bool:
        """Return whether the band covers ``level``, ``cause`` and ``category``.

        Returns:
            ``True`` for its levels and causes, and for its categories or
            any category when it names none.
        """
        return (
            level in self.levels
            and cause in self.causes
            and (not self.categories or category in self.categories)
        )

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
        for level, cause, category in _ladders(self.bands):
            ceilings = [
                b.up_to_months for b in self.bands if b.applies(level, cause, category)
            ]
            if not _grows(ceilings):
                msg = (
                    f"the notice bands of level {level} ({category}) on "
                    f"{cause.value} must grow in service, each ceiling once, "
                    "the last open-ended"
                )
                raise ValueError(msg)
        return self

    def band(
        self,
        level: str,
        cause: TerminationCause,
        months_of_service: int,
        category: WorkerCategory | None = None,
    ) -> NoticeBand | None:
        """Return the band of ``level``, ``cause`` and ``category`` for a service.

        Returns:
            The first band whose ceiling the service does not exceed;
            ``None`` when the CCNL sets no notice for the level, the cause or
            the category (an unknown category matches only the bands that
            name none).
        """
        return next(
            (
                b
                for b in self.bands
                if b.applies(level, cause, category)
                and (b.up_to_months is None or months_of_service <= b.up_to_months)
            ),
            None,
        )


def _ladders(
    bands: tuple[NoticeBand, ...],
) -> list[tuple[str, TerminationCause, WorkerCategory | None]]:
    """Return each level, cause and category whose bands make one ladder.

    Returns:
        The keys in a stable order; a band that names no category joins the
        ladder of every category another band names.
    """
    named = {k for b in bands for k in b.categories}
    keys = {
        (level, cause, category)
        for b in bands
        for level in b.levels
        for cause in b.causes
        for category in (b.categories or named or (None,))
    }
    return sorted(keys, key=str)


def _grows(ceilings: list[int | None]) -> bool:
    """Return whether the ceilings grow, each once, to one open end.

    Returns:
        ``True`` for distinct growing ceilings closed by a single ``None``.
    """
    bounded = [c for c in ceilings if c is not None]
    return (
        bounded == sorted(set(bounded))
        and ceilings[-1:] == [None]
        and ceilings.count(None) == 1
    )
