"""Default policies of the apprenticeship contract."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.default.models import FactEnforcement, absence_is_fact, requires_fact

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.default.models import FieldDefault


APPRENTICE_DEFAULTS: Mapping[str, FieldDefault] = {
    "Apprentice.programme": absence_is_fact(
        "a professionalising apprenticeship (D.Lgs. 81/2015 art. 44), the one "
        "the apprenticeship tracks of the CCNL pay"
    ),
    "Apprentice.school_year": requires_fact(
        "base_salary",
        "employment.contract_type.school_year",
        FactEnforcement.REPORTED,
        "unknown school year: a dual track paying by it raises a missing-fact error",
    ),
    "Apprentice.programme_months": requires_fact(
        "base_salary",
        "employment.contract_type.programme_months",
        FactEnforcement.REPORTED,
        "unknown programme length: a dual track paying by its half or length "
        "raises a missing-fact error",
    ),
    "Apprentice.hours": requires_fact(
        "base_salary",
        "employment.contract_type.hours",
        FactEnforcement.REPORTED,
        "unknown hours: a first- or third-level apprentice raises a missing-fact error",
    ),
    "Apprentice.ratei_hours": requires_fact(
        "base_salary",
        "employment.contract_type.ratei_hours",
        FactEnforcement.REPORTED,
        "unknown hours of the ratei: the final settlement of a first- or "
        "third-level apprentice liquidating extra months raises a "
        "missing-fact error",
    ),
    "Apprentice.track": requires_fact(
        "base_salary",
        "employment.contract_type.track",
        FactEnforcement.REPORTED,
        "the unique track of the level; several tracks raise an input error",
    ),
    "Apprentice.fixed_term": absence_is_fact(
        "a permanent apprenticeship (D.Lgs. 81/2015 art. 41 c. 1); a seasonal "
        "one with a term (art. 44 c. 5) is a fact the caller states"
    ),
    "Apprentice.failed_title_extension_start_month": absence_is_fact(
        "ordinary apprenticeship progression, or a competence-consolidation "
        "extension; a failed-title extension is a fact the caller states, "
        "and only a sourced first-level track can pay its previous-year phase"
    ),
}
