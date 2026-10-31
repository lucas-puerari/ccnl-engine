"""The statutory indemnities of maternity and work injury in the bundle."""

from __future__ import annotations

from functools import cache

from ccnl_engine.absence.insured.models import InsuredAbsenceRates
from ccnl_engine.sector.raw.loaders import _as_ruleset, _read_json

__all__ = ["load_insured_absence_rates"]

_FILE = "absence/insured/rates.json"


@cache
def load_insured_absence_rates() -> InsuredAbsenceRates:
    """Load the maternity and work-injury indemnities of the bundle.

    The file is not year- or sector-specific: the measures change only by
    primary legislation (D.Lgs. 151/2001, D.P.R. 1124/1965).

    Returns:
        The validated rates with the identity of the file.
    """
    raw = _read_json(_FILE)
    return InsuredAbsenceRates.model_validate({
        "maternity": raw["maternity"],
        "paternity": raw["paternity"],
        "parental": raw["parental"],
        "disability_permit": raw["disability_permit"],
        "nursing_rest": raw["nursing_rest"],
        "extraordinary_leave": raw["extraordinary_leave"],
        "injury": raw["injury"],
        "ruleset": _as_ruleset(raw),
    })
