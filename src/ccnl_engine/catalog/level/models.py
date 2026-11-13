"""One level of a CCNL as the catalog lists it."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.employment.category.models import WorkerCategory

__all__ = ["LevelSummary"]


@dataclass(frozen=True, slots=True)
class LevelSummary:
    """One level of a bundled CCNL, as ``Employment.level_code`` names it.

    Attributes:
        code: The level code (e.g. ``"C3"``).
        description: Label of the level in the CCNL data.
        category: Worker category the level is restricted to, ``None``
            when the level admits any.
        apprenticeship_tracks: Names of the apprenticeship tracks that lead
            to the level, the ``Apprentice.track`` a run may state.
        ladder: Career ladder of its own the level sits on (the operatori
            di vendita), ``None`` for the ordinary levels.
    """

    code: str
    description: str
    category: WorkerCategory | None
    apprenticeship_tracks: tuple[str, ...] = ()
    ladder: str | None = None
