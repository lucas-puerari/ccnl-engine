"""Canonical worker category (*categoria legale*, art. 2095 c.c.)."""

from enum import StrEnum

from ccnl_engine.engine.errors import InvalidInputError

__all__ = ["WorkerCategory", "parse_worker_category"]


class WorkerCategory(StrEnum):
    """Legal category of an employee under art. 2095 c.c.

    The single category vocabulary shared by CCNL data (levels, seniority
    rules, employer funds), INPS contribution rules and employment facts.
    Values are the lowercase Italian names used in the bundled JSON.

    Attributes:
        OPERAIO: Manual worker.
        IMPIEGATO: Clerical or technical employee.
        QUADRO: Middle manager (L. 190/1985).
        DIRIGENTE: Executive.
    """

    OPERAIO = "operaio"
    IMPIEGATO = "impiegato"
    QUADRO = "quadro"
    DIRIGENTE = "dirigente"


def parse_worker_category(value: WorkerCategory | str | None) -> WorkerCategory | None:
    """Return ``value`` as a :class:`WorkerCategory`, accepting its string value.

    Args:
        value: A member, its lowercase string value, or ``None``.

    Returns:
        The matching member, or ``None`` when ``value`` is ``None``.

    Raises:
        InvalidInputError: When ``value`` names no known category.
    """
    if value is None:
        return None
    try:
        return WorkerCategory(value)
    except ValueError:
        allowed = ", ".join(repr(c.value) for c in WorkerCategory)
        msg = f"unknown worker category {value!r}; expected one of {allowed}"
        raise InvalidInputError(msg, feature="worker_category") from None
