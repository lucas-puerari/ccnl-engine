"""The contribution on ending an employment, by year, from the bundle."""

from __future__ import annotations

from functools import cache

from pydantic import ValidationError

from ccnl_engine.errors import DataIntegrityError, UnsupportedTaxYearError
from ccnl_engine.sector.raw.loaders import _try_ruleset, read_year_json
from ccnl_engine.termination.naspi.models import NaspiDismissalRules

__all__ = ["load_naspi_dismissal_rules"]


@cache
def load_naspi_dismissal_rules(year: int) -> NaspiDismissalRules | None:
    """Load the contribution of L. 92/2012 art. 2 c. 31 for *year*.

    Returns:
        The rules, or ``None`` when the bundle has no file for *year* (the
        NASpI maximum of the year is not published yet).

    Raises:
        DataIntegrityError: When the file is not valid or of another year.
    """
    filename = f"termination/naspi/{year}.json"
    try:
        raw = read_year_json(filename, year)
    except UnsupportedTaxYearError:
        return None
    try:
        rules = NaspiDismissalRules.model_validate({
            **{k: v for k, v in raw.items() if k != "description"},
            "ruleset": _try_ruleset(raw),
        })
    except ValidationError as exc:
        msg = f"{filename} is not a valid NASpI dismissal table: {exc}"
        raise DataIntegrityError(msg) from exc
    if rules.year != year:
        msg = f"{filename} year={rules.year!r} does not match requested year={year!r}"
        raise DataIntegrityError(msg)
    return rules
