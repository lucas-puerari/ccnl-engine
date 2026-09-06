"""Shared primitive types and validation helpers used across ccnl_engine."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Bracket:
    """A rate bracket with an optional upper bound.

    Used for IRPEF marginal brackets and surtax brackets. When up_to
    is None the bracket covers all income above the previous boundary.
    """

    up_to: Decimal | None
    rate: Decimal


def validate_open_sequence[T](
    items: Sequence[T],
    get_start: Callable[[T], object],
    get_end: Callable[[T], object | None],
    label: str,
) -> None:
    """Assert that items form an ordered, contiguous, open-ended sequence.

    Each item's end must equal the next item's start. Only the last item
    may have no end.

    Raises:
        ValueError: If the sequence is empty, has a non-last open item,
            has a gap between items, or has a bounded last item.
    """
    if not items:
        msg = f"{label}: sequence must not be empty"
        raise ValueError(msg)
    for i, item in enumerate(items[:-1]):
        end = get_end(item)
        if end is None:
            msg = f"{label}[{i}]: only the last item may have no end"
            raise ValueError(msg)
        next_start = get_start(items[i + 1])
        if end != next_start:
            msg = f"{label}[{i}]: end {end!r} does not match next start {next_start!r}"
            raise ValueError(msg)
    if get_end(items[-1]) is not None:
        msg = f"{label}: last item must have no end (open-ended)"
        raise ValueError(msg)


def assert_ivs_le_total(
    ivs_name: str,
    ivs_val: Decimal,
    total_name: str,
    total_val: Decimal,
) -> None:
    """Assert that an IVS rate does not exceed its total rate.

    Raises:
        ValueError: If ivs_val exceeds total_val.
    """
    if ivs_val > total_val:
        msg = f"{ivs_name} ({ivs_val}) must not exceed {total_name} ({total_val})"
        raise ValueError(msg)
