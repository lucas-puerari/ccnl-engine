"""Rules of the yearly TFR revaluation and of the TFR settlement from the bundle."""

from __future__ import annotations

from functools import cache

from pydantic import ValidationError

from ccnl_engine.errors import DataIntegrityError, UnsupportedTaxYearError
from ccnl_engine.sector.raw.loaders import _try_ruleset, read_year_json
from ccnl_engine.severance.revaluation.models import TfrRevaluationRules
from ccnl_engine.severance.settlement.models import TfrSettlementRules


def _load_year_file[T: (TfrRevaluationRules, TfrSettlementRules)](
    dataset: str, year: int, model: type[T], label: str
) -> T | None:
    """Load ``knowledge/{dataset}/{year}.json`` validated by *model*.

    Returns:
        The validated rules, or ``None`` when the bundle has no file for
        *year*.

    Raises:
        DataIntegrityError: If the file's ``year`` does not match *year* or
            the file is not valid.
    """
    filename = f"{dataset}/{year}.json"
    try:
        raw = read_year_json(filename, year)
    except UnsupportedTaxYearError:
        return None
    try:
        rules = model.model_validate({
            **{k: v for k, v in raw.items() if k != "description"},
            "ruleset": _try_ruleset(raw),
        })
    except ValidationError as exc:
        msg = f"{filename} is not a valid {label}: {exc}"
        raise DataIntegrityError(msg) from exc
    if rules.year != year:
        msg = f"{filename} year={rules.year!r} does not match requested year={year!r}"
        raise DataIntegrityError(msg)
    return rules


@cache
def load_tfr_settlement_rules(year: int) -> TfrSettlementRules | None:
    """Load the separate taxation rules of the TFR paid on termination in *year*.

    The file ``knowledge/severance/settlement/{year}.json`` carries the
    multiplier of the reference income of art. 19 c. 1 TUIR and the
    counting of the months of service of art. 2120 c. 1 c.c., with their
    sources.  A year without a file has no computed settlement.

    Args:
        year: Year of the termination (e.g. ``2026``).

    Returns:
        The validated rules, or ``None`` when the bundle has no file for
        *year*.
    """
    return _load_year_file(
        "severance/settlement", year, TfrSettlementRules, "TFR settlement table"
    )


@cache
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
        *year*; a file that is not a valid revaluation table of *year*
        raises ``DataIntegrityError``.
    """
    return _load_year_file(
        "severance/revaluation", year, TfrRevaluationRules, "TFR revaluation table"
    )
