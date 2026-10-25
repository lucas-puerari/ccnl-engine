"""Work-income deduction constants of a tax year from the bundle."""

from __future__ import annotations

from pydantic import ValidationError

from ccnl_engine.errors import DataIntegrityError
from ccnl_engine.irpef.models import WorkDeductionRules
from ccnl_engine.sector.raw.loaders import read_year_json


def load_work_deduction_rules(year: int) -> WorkDeductionRules:
    """Load the art. 13 TUIR constants for *year*.

    The file ``knowledge/irpef/work_deduction/{year}.json`` holds them.
    They are statutory and the same for every sector, so one file per year
    carries them with its own ruleset, apart from the sector tax files; a
    constant it does not state fails the load instead of taking a default.

    Args:
        year: Fiscal year (e.g. ``2026``).

    Returns:
        The validated constants, with their provenance.

    Raises:
        DataIntegrityError: If the file's ``year`` does not match *year* or
            the file is not a valid table of the constants.
    """
    filename = f"irpef/work_deduction/{year}.json"
    raw = read_year_json(filename, year)
    if raw.get("year") != year:
        msg = (
            f"{filename} year={raw.get('year')!r} "
            f"does not match requested year={year!r}"
        )
        raise DataIntegrityError(msg)
    try:
        return WorkDeductionRules.model_validate(raw["work_deduction"])
    except (KeyError, ValidationError) as exc:
        msg = f"{filename} is not a valid work deduction table: {exc!r}"
        raise DataIntegrityError(msg) from exc
