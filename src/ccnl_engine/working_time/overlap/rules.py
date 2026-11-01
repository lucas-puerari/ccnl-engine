"""Whether two bands of a CCNL can apply to the same worker."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

__all__ = ["bands_overlap"]

_KEYS = ("levels", "subsectors", "categories")


def bands_overlap(bands: Sequence[object]) -> bool:
    """Return whether two of ``bands`` can apply to the same worker.

    Returns:
        ``True`` when two bands share a level, a sub-sector and a category,
        a band naming none of one sharing every value.
    """
    return any(
        all(_meet(getattr(band, k, ()), getattr(other, k, ())) for k in _KEYS)
        for i, band in enumerate(bands)
        for other in bands[i + 1 :]
    )


def _meet(first: Sequence[object], second: Sequence[object]) -> bool:
    return not first or not second or bool(set(first) & set(second))
