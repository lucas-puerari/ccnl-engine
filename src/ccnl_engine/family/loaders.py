"""Art. 12 TUIR family deduction rules of a tax year from the bundle."""

from __future__ import annotations

from pydantic import ValidationError

from ccnl_engine.errors import DataIntegrityError
from ccnl_engine.family.models import FamilyDeductionRules
from ccnl_engine.knowledge.sector.raw.loaders import _try_ruleset, read_year_json


def load_family_deduction_rules(year: int) -> FamilyDeductionRules:
    """Load Art. 12 TUIR family deduction rules for *year*.

    The file ``knowledge/family/{year}.json`` carries
    spouse, children and other-dependent deduction parameters.  These are
    pure law, not CCNL-specific.

    Args:
        year: Fiscal year (e.g. ``2026``).

    Returns:
        A :class:`~ccnl_engine.family.models.FamilyDeductionRules`
        with all deduction parameters validated.

    Raises:
        DataIntegrityError: If the file's ``year`` field does not match *year*.
    """
    filename = f"family/{year}.json"
    raw = read_year_json(filename, year)
    if raw.get("year") != year:
        msg = (
            f"{filename} year={raw.get('year')!r} "
            f"does not match requested year={year!r}"
        )
        raise DataIntegrityError(msg)

    try:
        return FamilyDeductionRules.model_validate({
            **raw,
            "ruleset": _try_ruleset(raw),
        })
    except ValidationError as exc:
        msg = f"{filename} is not a valid family deduction table: {exc}"
        raise DataIntegrityError(msg) from exc
