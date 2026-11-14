"""Defaults of the parental leave facts read past the indemnified months."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.default.models import FactEnforcement, requires_fact

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.default.models import FieldDefault

_INCOME = (
    "unknown individual income of the parent: a day past the indemnified months "
    "(art. 34 c. 3 D.Lgs. 151/2001) is paid nothing, with a missing_fact "
    "individual_income blocker"
)

PARENTAL_DEFAULTS: Mapping[str, FieldDefault] = {
    "ParentalLeaveEvent.individual_income": requires_fact(
        "parental_leave", "event.individual_income", FactEnforcement.REPORTED, _INCOME
    ),
    "HourlyParentalLeaveEvent.individual_income": requires_fact(
        "parental_leave", "event.individual_income", FactEnforcement.REPORTED, _INCOME
    ),
}
