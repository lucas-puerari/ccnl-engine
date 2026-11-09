"""Default policies for worker roles and former-worker holiday compensation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.default.models import FactEnforcement, requires_fact

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.default.models import FieldDefault


ROLE_DEFAULTS: Mapping[str, FieldDefault] = {
    "Employment.holiday_company_offset": requires_fact(
        "base_salary",
        "employment.holiday_company_offset",
        FactEnforcement.REPORTED,
        "unknown company holiday compensation: a Confapi former legal operaio "
        "with an eligible weekday holiday or weekend Epiphany has a "
        "missing_fact holiday_company_offset blocker; zero states none",
    ),
    "Employment.roles": requires_fact(
        "base_salary",
        "employment.roles",
        FactEnforcement.REPORTED,
        "unknown roles: a run whose level has an allowance restricted to a role "
        "in force leaves it out and has a missing_fact roles blocker; a "
        "supplement the CCNL pays apart for a role is not derived; an empty "
        "set states that the worker holds no role",
    ),
}
