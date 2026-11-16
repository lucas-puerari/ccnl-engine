"""Default policies for worker roles, former-worker holidays and garnishments."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.default.models import FactEnforcement, requires_fact

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.default.models import FieldDefault


ROLE_DEFAULTS: Mapping[str, FieldDefault] = {
    "PersonalWithholding.installment": requires_fact(
        "personal_withholdings",
        "personal_withholdings.installment",
        FactEnforcement.REPORTED,
        "a garnishment takes the legal fraction; two of one kind without their "
        "ordinanze's amounts (art. 553 c.p.c.) report an installment blocker",
    ),
    "Employment.holiday_company_offset": requires_fact(
        "base_salary",
        "employment.holiday_company_offset",
        FactEnforcement.REPORTED,
        "unknown company holiday compensation: a Confapi former legal operaio "
        "with an eligible weekday holiday or weekend Epiphany has a "
        "missing_fact holiday_company_offset blocker; zero states none",
    ),
    "Employment.fund_opt_ins": requires_fact(
        "contractual_funds",
        "employment.fund_opt_ins",
        FactEnforcement.REPORTED,
        "unknown choice of a fund that covers only the worker paying its "
        "worker share (Alimentari FASA from 1 June 2029): nothing is posted "
        "for it, with a missing_fact fund_opt_ins blocker; an empty set "
        "states that the worker pays none",
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
