"""Validators of the public collections: tuples, frozensets and mappings.

A collection of a public input is validated element by element, each
element reported by its position (``"PeriodFacts.events[2]"``) or its key
(``"YearInput.periods[6]"``), and normalised to a tuple, a frozenset or a
dict only after every element passed.  Rejections go through
:func:`~ccnl_engine.shared.domain.validation.reject`, so they carry the
same field, feature and remediation as the scalar validators.
"""

from __future__ import annotations

import reprlib
from collections.abc import Callable, Mapping

from ccnl_engine.shared.domain.validation import reject, type_names

__all__ = ["Item", "frozenset_of", "items_of_type", "mapping_of", "tuple_of"]

#: Validator of one element of a collection: the element and its path in,
#: the validated element out.
type Item[T] = Callable[[object, str], T]

_REPR = reprlib.Repr(maxstring=60, maxother=60)


def items_of_type[T](
    expected: type[T] | tuple[type[T], ...],
    *,
    feature: str,
    name: str | None = None,
) -> Item[T]:
    """Return the validator of elements that must be instances of ``expected``.

    Args:
        expected: The accepted class, or classes.
        feature: Feature of the input.
        name: What an element must be in the error, e.g. ``"a WorkEvent"``;
            defaults to the names of ``expected``.

    Returns:
        A validator that rejects any other element.
    """
    description = type_names(expected) if name is None else name

    def item(value: object, path: str) -> T:
        if not isinstance(value, expected):
            reject(path, description, value, feature=feature)
        return value

    return item


def tuple_of[T](
    value: object, path: str, item: Item[T], *, feature: str
) -> tuple[T, ...]:
    """Validate a tuple or a list element by element and return it as a tuple.

    An element rejected by ``item`` is reported as ``path[index]``.

    Returns:
        The validated elements, in order.
    """
    if not isinstance(value, tuple | list):
        reject(path, "a tuple or a list", value, feature=feature)
    return tuple(item(element, f"{path}[{i}]") for i, element in enumerate(value))


def frozenset_of[T](
    value: object, path: str, item: Item[T], *, feature: str
) -> frozenset[T]:
    """Validate a frozenset element by element and return it.

    A mutable ``set`` is rejected: the input is immutable.

    An element rejected by ``item`` is reported as ``path[element]``.

    Returns:
        The validated elements.
    """
    if not isinstance(value, frozenset):
        reject(path, "a frozenset", value, feature=feature)
    return frozenset(item(e, f"{path}[{_REPR.repr(e)}]") for e in value)


def mapping_of[K, V](
    value: object,
    path: str,
    key: Item[K],
    item: Item[V],
    *,
    feature: str,
) -> dict[K, V]:
    """Validate a mapping key by key and value by value and return a dict.

    A rejected key or value is reported as ``path[key]``.

    Returns:
        The validated entries, in the order of ``value``.
    """
    if not isinstance(value, Mapping):
        reject(path, "a mapping", value, feature=feature)
    entries: dict[K, V] = {}
    for raw_key, raw_value in value.items():
        entry = f"{path}[{_REPR.repr(raw_key)}]"
        entries[key(raw_key, entry)] = item(raw_value, entry)
    return entries
