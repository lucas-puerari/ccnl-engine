"""Defaults of the fields of :class:`~ccnl_engine.inputs.Apprentice`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.default.models import FactEnforcement, absence_is_fact, requires_fact

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.default.models import FieldDefault

__all__ = ["APPRENTICE_DEFAULTS"]

_REPORTED = FactEnforcement.REPORTED

#: Classification of each defaulted field of an apprenticeship.
APPRENTICE_DEFAULTS: Mapping[str, FieldDefault] = {
    "Apprentice.programme": absence_is_fact(
        "a professionalising apprenticeship (D.Lgs. 81/2015 art. 44), the one "
        "the apprenticeship tracks of the CCNL pay"
    ),
    "Apprentice.school_year": requires_fact(
        "base_salary",
        "employment.contract_type.school_year",
        _REPORTED,
        "unknown school year: a dual track paying by it raises a missing-fact error",
    ),
    "Apprentice.programme_months": requires_fact(
        "base_salary",
        "employment.contract_type.programme_months",
        _REPORTED,
        "unknown programme length: a dual track paying by its half or length "
        "raises a missing-fact error",
    ),
    "Apprentice.hours": requires_fact(
        "base_salary",
        "employment.contract_type.hours",
        _REPORTED,
        "unknown hours: a first- or third-level apprentice raises a missing-fact error",
    ),
    "Apprentice.track": requires_fact(
        "base_salary",
        "employment.contract_type.track",
        _REPORTED,
        "the unique track of the level; several tracks raise an input error",
    ),
}
