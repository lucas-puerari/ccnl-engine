"""Shared primitive types and validation helpers used across ccnl_engine."""

from __future__ import annotations

import copy
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from decimal import Decimal
from typing import Any


class FrozenDict[K, V](dict[K, V]):  # noqa: FURB189
    """Immutable dict that serializes as a plain dict and supports deepcopy.

    Pydantic treats this as a regular dict for JSON serialization because it
    is a dict subclass (``isinstance(fd, dict)`` is ``True``).  Unlike
    :class:`types.MappingProxyType`, it supports ``copy.deepcopy`` and
    ``model_copy(deep=True)`` without pickling errors, while still blocking
    all in-place mutations via the public API.

    ``dict`` is subclassed intentionally — the ``FURB189`` noqa is required
    because :class:`collections.UserDict` is not recognised as a ``dict`` by
    Pydantic's JSON serialiser.

    **Known limitation**: the overrides guard against *accidental* mutation
    only.  Bypassing them via the base class (``dict.__setitem__(fd, k, v)``)
    is technically possible and not blocked.  :class:`FrozenDict` is not a
    security boundary; callers must not rely on it for that purpose.
    """

    __slots__ = ()

    def __setitem__(self, _key: Any, _value: Any) -> None:  # noqa: ANN401
        """Raise TypeError on item assignment.

        Raises:
            TypeError: Always.
        """
        msg = f"'{type(self).__name__}' object does not support item assignment"
        raise TypeError(msg)

    def __delitem__(self, _key: Any) -> None:  # noqa: ANN401
        """Raise TypeError on item deletion.

        Raises:
            TypeError: Always.
        """
        msg = f"'{type(self).__name__}' object does not support item deletion"
        raise TypeError(msg)

    def update(
        self,
        *_args: Any,  # noqa: ANN401
        **_kwargs: Any,  # noqa: ANN401
    ) -> None:
        """Raise TypeError on update.

        Raises:
            TypeError: Always.
        """
        msg = f"'{type(self).__name__}' object does not support update"
        raise TypeError(msg)

    def pop(self, *_args: Any) -> V:  # noqa: ANN401
        """Raise TypeError on pop.

        Raises:
            TypeError: Always.
        """
        msg = f"'{type(self).__name__}' object does not support pop"
        raise TypeError(msg)

    def popitem(self) -> tuple[K, V]:
        """Raise TypeError on popitem.

        Raises:
            TypeError: Always.
        """
        msg = f"'{type(self).__name__}' object does not support popitem"
        raise TypeError(msg)

    def clear(self) -> None:
        """Raise TypeError on clear.

        Raises:
            TypeError: Always.
        """
        msg = f"'{type(self).__name__}' object does not support clear"
        raise TypeError(msg)

    def setdefault(
        self,
        _key: Any,  # noqa: ANN401
        _default: Any = None,  # noqa: ANN401
    ) -> V:
        """Raise TypeError on setdefault.

        Raises:
            TypeError: Always.
        """
        msg = f"'{type(self).__name__}' object does not support setdefault"
        raise TypeError(msg)

    def __ior__(  # type: ignore[override, misc]
        self,
        _other: Any,  # noqa: ANN401
    ) -> FrozenDict[K, V]:
        """Raise TypeError on in-place |=.

        Raises:
            TypeError: Always.
        """
        msg = f"'{type(self).__name__}' object does not support |="
        raise TypeError(msg)

    def __deepcopy__(self, memo: dict[int, Any]) -> FrozenDict[K, V]:
        """Return a deepcopy by copying the underlying dict data.

        Bypasses the frozen ``__setitem__`` by constructing a new
        :class:`FrozenDict` from a plain-dict deepcopy.

        Returns:
            A new :class:`FrozenDict` with deepcopied values.
        """
        return FrozenDict(copy.deepcopy(dict(self), memo))

    def __repr__(self) -> str:
        """Return a repr identifying this as a FrozenDict.

        Returns:
            A string of the form ``FrozenDict({...})`.
        """
        return f"FrozenDict({dict.__repr__(self)})"


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
