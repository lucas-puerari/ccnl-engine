"""Allowances the CCNL leaves out of the TFR base.

Art. 2120 c. 2 c.c.: the TFR counts every sum paid "salvo diversa
previsione dei contratti collettivi".  The CCNL of the dirigenza medica e
veterinaria leaves the indennità di specificità medico-veterinaria
(728.15) out of it: the TFR base of the dirigente is the minimum alone,
3846.60, and so is the end-of-service base of a public employee.

January 2026, hired that month, gross 3846.60 + 728.15 = 4574.75:

- TFR at the employer: TFR base 3846.60;
- TFS (INADEL, the CPS): base 80% of 3846.60 = 3077.28, worker 2.50% =
  76.932 -> 76.93, administration 3.60% = 110.78208 -> 110.78.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import Employment
from ccnl_engine.inputs import NoPensionFund, Permanent, PublicEndOfService
from tests.knowledge.ccnl_engine.payroll.employment.builders_seniority import new_hire
from tests.knowledge.ccnl_engine.payroll.support import regular_period
from tests.knowledge.ccnl_engine.payroll.taxation.builders_current_year import (
    employment_only,
)

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult

pytestmark = pytest.mark.legal_scenario


def _january(regime: PublicEndOfService) -> PeriodResult:
    employment = Employment(
        ccnl_slug="dirigenza-sanitaria-medico-veterinaria-aran.json",
        level_code="DIRIGENTE",
        seniority=new_hire(),
        pension_fund=NoPensionFund(),
        contract_type=Permanent(),
        public_end_of_service=regime,
    )
    return regular_period(employment=employment, current_year=employment_only())


def test_tfr_base_leaves_the_specificita_out() -> None:
    """3846.60 of a gross of 4574.75."""
    result = _january(PublicEndOfService.TFR_EMPLOYER)
    assert result.period_gross == Decimal("4574.75")
    (tfr,) = [d for d in result.decisions if d.capability == "tfr"]
    assert tfr.inputs["base"] == Decimal("3846.60")


def test_end_of_service_base_leaves_it_out_too() -> None:
    """INADEL on 80% of 3846.60: 76.93 and 110.78."""
    result = _january(PublicEndOfService.TFS)
    components = {c.name: c for c in result.contribution_breakdown.components}
    assert components["tfs_employee"].base == Decimal("3077.28")
    assert components["tfs_employee"].amount == Decimal("76.93")
    assert components["tfs_employer"].amount == Decimal("110.78")
