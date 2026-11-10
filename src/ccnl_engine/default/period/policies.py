"""Defaults of the end of an employment (:class:`EmploymentPeriod`)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.default.models import FactEnforcement, requires_fact

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.default.models import FieldDefault

__all__ = ["PERIOD_DEFAULTS"]

_REPORTED = FactEnforcement.REPORTED

#: Classification of each defaulted field of the end of an employment.
PERIOD_DEFAULTS: Mapping[str, FieldDefault] = {
    "EmploymentPeriod.ended_by": requires_fact(
        "termination_notice",
        "employment.employment_period.ended_by",
        _REPORTED,
        "an end of the employment whose cause is not stated: the notice "
        "indemnity and the NASpI contribution have a missing_fact ended_by "
        "blocker",
    ),
    "EmploymentPeriod.just_cause": requires_fact(
        "termination_notice",
        "employment.employment_period.just_cause",
        _REPORTED,
        "a dismissal or a resignation whose just cause is not stated: the "
        "notice indemnity, and the NASpI contribution of a resignation, have "
        "a missing_fact just_cause blocker",
    ),
    "EmploymentPeriod.disciplinary_dismissal": requires_fact(
        "base_salary",
        "employment.employment_period.disciplinary_dismissal",
        _REPORTED,
        "a vested loyalty award on a dismissal whose disciplinary status is "
        "not stated: the dismissal twelfths have a missing_fact "
        "disciplinary_dismissal blocker",
    ),
    "EmploymentPeriod.naspi_case": requires_fact(
        "naspi_dismissal",
        "employment.employment_period.naspi_case",
        _REPORTED,
        "an end whose NASpI case is not stated: the contribution is read "
        "from the cause and the just cause alone, with a provisional "
        "naspi_dismissal_case_unknown issue",
    ),
}
