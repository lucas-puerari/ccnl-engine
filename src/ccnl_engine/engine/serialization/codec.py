"""Shared codec primitives used by both the snapshot and result encoders."""

_STRICT_PRIMITIVES: frozenset[type] = frozenset({bool, int, str})


def _validate_primitive(raw: object, hint: type) -> object:
    """Validate *raw* against a strict primitive *hint* and return it unchanged.

    ``bool`` is checked before ``int`` because ``bool`` is a subclass of
    ``int`` in Python and the two must not be confused.

    Returns:
        *raw* when it matches *hint* exactly.

    Raises:
        TypeError: When *raw* does not match the exact primitive *hint*.
    """
    if hint is bool:
        if not isinstance(raw, bool):
            msg = f"expected bool, got {type(raw).__name__!r}"
            raise TypeError(msg)
    elif hint is int:
        if not isinstance(raw, int) or isinstance(raw, bool):
            msg = f"expected int, got {type(raw).__name__!r}"
            raise TypeError(msg)
    elif not isinstance(raw, str):
        msg = f"expected str, got {type(raw).__name__!r}"
        raise TypeError(msg)
    return raw
