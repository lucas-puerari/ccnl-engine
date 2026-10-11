"""Somma esente rules of a tax year from the bundle."""

from __future__ import annotations

from pydantic import ValidationError

from ccnl_engine.errors import DataIntegrityError
from ccnl_engine.sector.raw.loaders import _as_ruleset, read_year_json
from ccnl_engine.tax_credit.models import SommaEsenteRules


def load_somma_esente_rules(year: int) -> SommaEsenteRules:
    """Load the somma esente of L. 207/2024 art. 1 cc. 4-5 for *year*.

    The file ``knowledge/tax_credit/somma_esente/{year}.json`` holds the
    bands of c. 4.  They are statutory and the same for every sector, so
    the file carries its own ruleset, apart from the sector tax files.

    Args:
        year: Fiscal year (e.g. ``2026``).

    Returns:
        The validated bands, with their provenance and the ruleset of the
        file.

    Raises:
        DataIntegrityError: If the file's ``year`` does not match *year* or
            the file is not a valid somma esente table.
    """
    filename = f"tax_credit/somma_esente/{year}.json"
    raw = read_year_json(filename, year)
    if raw.get("year") != year:
        msg = (
            f"{filename} year={raw.get('year')!r} "
            f"does not match requested year={year!r}"
        )
        raise DataIntegrityError(msg)
    try:
        return SommaEsenteRules.model_validate({
            **raw["somma_esente"],
            "ruleset": _as_ruleset(raw),
        })
    except (KeyError, ValidationError) as exc:
        msg = f"{filename} is not a valid somma esente table: {exc!r}"
        raise DataIntegrityError(msg) from exc
