"""Apprenticeship contract, whose pay the CCNL apprenticeship rules derive."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from ccnl_engine.validators import require_int, require_str

__all__ = ["Apprentice"]

_CONTRACT_FEATURE = "contract_type"


@dataclass(frozen=True, slots=True)
class Apprentice:
    """Apprenticeship contract; salary is derived from CCNL apprenticeship rules.

    Attributes:
        months_elapsed: Months of apprenticeship service elapsed so far,
            ``>= 0``.  Used to look up the applicable ``apprenticeship_pct``
            in the CCNL percentage track, or the under-classification level
            in under-classification tracks.
        track: Name of the CCNL apprenticeship track to apply. Required
            only when more than one track covers the destination level;
            ``None`` lets the engine select the unique applicable track.

    Raises:
        InvalidInputError: When ``months_elapsed`` is not a non-negative
            int or ``track`` is not a non-blank string.
    """

    months_elapsed: int
    track: str | None = None
    type: Literal["apprentice"] = field(default="apprentice", init=False)

    def __post_init__(self) -> None:  # noqa: D105
        require_int(
            self.months_elapsed,
            "Apprentice.months_elapsed",
            feature=_CONTRACT_FEATURE,
            minimum=0,
        )
        require_str(
            self.track,
            "Apprentice.track",
            feature=_CONTRACT_FEATURE,
            non_blank=True,
            optional=True,
        )
