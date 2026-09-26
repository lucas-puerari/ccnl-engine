"""Construction checks of a period calculation request.

A request can come from an untyped caller (a JSON payload, a notebook).
These checks describe a value of the wrong type, or a regular run outside
the employment, so that the request raises ``InvalidInputError`` at
construction instead of an ``AttributeError`` or a silent result deep in
the calculation.  They return the problem; :func:`raise_on` raises it
with the feature of the input that found it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.run import RunKind
from ccnl_engine.shared.domain.errors import InvalidInputError

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ccnl_engine.payroll.domain.employment_facts import EmploymentPeriod
    from ccnl_engine.payroll.domain.period_payroll import PeriodId
    from ccnl_engine.payroll.domain.run import PayrollRun

__all__ = ["FieldSpec", "employment_gap", "raise_on", "type_error"]

#: A request field to check: name, value, accepted types, ``None`` accepted.
type FieldSpec = tuple[str, object, type | tuple[type, ...], bool]


def type_error(fields: Iterable[FieldSpec]) -> str | None:
    """Describe the first field that is not of its expected type.

    Args:
        fields: The fields to check, in order.

    Returns:
        A message naming the field, the expected and the supplied type, or
        ``None`` when every field is of its type.
    """
    for name, value, expected, optional in fields:
        if (optional and value is None) or isinstance(value, expected):
            continue
        types = expected if isinstance(expected, tuple) else (expected,)
        names = " or ".join(t.__name__ for t in types)
        return f"{name} must be {names}; got {type(value).__name__} {value!r}"
    return None


def raise_on(problem: str | None, feature: str) -> None:
    """Raise ``InvalidInputError`` for ``problem`` when there is one.

    Raises:
        InvalidInputError: When ``problem`` is not ``None``.
    """
    if problem is not None:
        raise InvalidInputError(problem, feature=feature)


def employment_gap(
    period_id: PeriodId,
    run: PayrollRun | None,
    employment: EmploymentPeriod | None,
) -> str | None:
    """Describe a regular run for a month without a day of employment.

    Args:
        period_id: Competence month of the run.
        run: The run, ``None`` for the regular run of the month.
        employment: Employment period, ``None`` when not tracked.

    Returns:
        A message when the run is regular and ``employment`` has no day in
        its month, otherwise ``None``.
    """
    regular = run is None or run.run_kind is RunKind.REGULAR
    if (
        employment is None
        or not regular
        or employment.overlaps_month(period_id.year, period_id.month)
    ):
        return None
    return (
        f"regular run {period_id.year}-{period_id.month:02d} is outside the "
        f"employment ({employment.started_on} to {employment.ended_on})"
    )
