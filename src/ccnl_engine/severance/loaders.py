"""Rules of the yearly TFR revaluation of a tax year from the bundle."""

from __future__ import annotations

from pydantic import ValidationError

from ccnl_engine.errors import DataIntegrityError, UnsupportedTaxYearError
from ccnl_engine.knowledge.sector.raw.loaders import _try_ruleset, read_year_json
from ccnl_engine.severance.revaluation.models import TfrRevaluationRules


def load_tfr_revaluation_rules(year: int) -> TfrRevaluationRules | None:
    """Load the TFR revaluation rules at 31 December of *year*.

    The file ``knowledge/severance/revaluation/{year}.json`` carries the
    rate of art. 2120 c. 4 c.c., the ISTAT FOI indexes it is computed from
    and the substitute tax of D.Lgs. 47/2000 art. 11.  These are pure law
    and statistics, not sector-specific.

    Args:
        year: Year of the revaluation (e.g. ``2026``).

    Returns:
        The validated rules, or ``None`` when the bundle has no file for
        *year*.

    Raises:
        DataIntegrityError: If the file's ``year`` does not match *year* or
            the file is not a valid revaluation table.
    """
    filename = f"severance/revaluation/{year}.json"
    try:
        raw = read_year_json(filename, year)
    except UnsupportedTaxYearError:
        return None
    try:
        rules = TfrRevaluationRules.model_validate({
            **{k: v for k, v in raw.items() if k != "description"},
            "ruleset": _try_ruleset(raw),
        })
    except ValidationError as exc:
        msg = f"{filename} is not a valid TFR revaluation table: {exc}"
        raise DataIntegrityError(msg) from exc
    if rules.year != year:
        msg = f"{filename} year={rules.year!r} does not match requested year={year!r}"
        raise DataIntegrityError(msg)
    return rules
