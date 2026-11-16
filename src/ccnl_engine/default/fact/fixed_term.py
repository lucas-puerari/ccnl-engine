"""Defaults of the fixed-term contract."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.default.models import FactEnforcement, requires_fact

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.default.models import FieldDefault

__all__ = ["FIXED_TERM_DEFAULTS"]

FIXED_TERM_DEFAULTS: Mapping[str, FieldDefault] = {
    "FixedTerm.renewals": requires_fact(
        "inps_employer",
        "employment.contract_type.renewals",
        FactEnforcement.REPORTED,
        "unknown renewals: a run that owes the 0.5-point increase of the NASpI "
        "surcharge per renewal (L. 92/2012 art. 2 c. 28) has a missing_fact "
        "renewals blocker",
    ),
    "FixedTerm.naspi_exclusion": requires_fact(
        "inps_employer",
        "employment.contract_type.naspi_exclusion",
        FactEnforcement.REPORTED,
        "unknown exclusion: a run whose sector charges the NASpI surcharge "
        "(L. 92/2012 art. 2 c. 28-29) has a missing_fact naspi_exclusion "
        "blocker",
    ),
    "FixedTerm.qualifying_years": requires_fact(
        "base_salary",
        "employment.contract_type.qualifying_years",
        FactEnforcement.REPORTED,
        "unknown years: a run that pays an hourly percentage gated by them "
        "(operai agricoli art. 54-bis, from 2027) raises "
        "MissingRequiredFactError; other runs do not read it",
    ),
}
