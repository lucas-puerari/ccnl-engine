"""Validation of counted presence days on payroll requests."""

from ccnl_engine.errors import InvalidInputError


def validate_presence_days(
    work_days: int | None, site_days: int | None, *, owner: str
) -> None:
    """Check nonnegative days and that site days are a subset of work days.

    Raises:
        InvalidInputError: On a non-integer, a count outside 0..31, or a
            site count greater than the corresponding work count.
    """
    for name, value in (
        ("presence_days", work_days),
        ("site_presence_days", site_days),
    ):
        if value is not None and (type(value) is not int or not 0 <= value <= 31):
            msg = f"{owner}.{name} must be between 0 and 31"
            raise InvalidInputError(
                msg, field=f"{owner}.{name}", feature="period_facts"
            )
    if work_days is not None and site_days is not None and site_days > work_days:
        msg = f"{owner}.site_presence_days cannot exceed presence_days"
        raise InvalidInputError(
            msg, field=f"{owner}.site_presence_days", feature="period_facts"
        )
