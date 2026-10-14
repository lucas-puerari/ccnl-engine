"""The IVS massimale of a public employee caps the credit and ASV too.

L. 335/1995 art. 2 c. 18 caps the pension base of a worker first enrolled
after 1995 at 122,295 EUR in 2026 (INPS circ. 6/2026).  The INPS page "I
contributi dei dipendenti pubblici" computes the Gestione credito
contribution (0.35%, L. 662/1996 art. 1 c. 242) "nei limiti del massimale
contributivo eventualmente applicabile al lavoratore", and the Assicurazione
Sociale Vita takes the base "coincidente con quella assoggettata alla
contribuzione ai fini pensionistici" (INPS circ. 104/2014 par. 3.1).

Funzioni Centrali, Funzionari, November 2026, 2,227.99 of base (the public
management keeps the cents), with 121,500 of the year already contributed:
795 of headroom.  Credit 0.35% of 795 = 2.78; ASV 0.027% = 0.21 of the
worker and 0.093% = 0.74 of the employer.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import Employment
from ccnl_engine.balance.competence.models import EmploymentAccrualState
from ccnl_engine.balance.models import PeriodState
from ccnl_engine.contribution.base.models import InpsBaseYtd
from ccnl_engine.inputs import (
    ContributionHistory,
    NoPensionFund,
    Permanent,
    PublicEndOfService,
)
from tests.knowledge.ccnl_engine.irpef.other_income.builders import (
    employment_only,
)
from tests.knowledge.ccnl_engine.seniority.builders import new_hire
from tests.knowledge.ccnl_engine.support import EMPLOYER, regular_period

pytestmark = pytest.mark.legal_scenario

_HEADROOM = Decimal("795.00")


def _components(enrolled_on: date) -> dict[str, tuple[Decimal, Decimal]]:
    employment = Employment(
        ccnl_slug="funzioni-centrali-aran.json",
        level_code="FUNZIONARI",
        seniority=new_hire(),
        pension_fund=NoPensionFund(),
        contract_type=Permanent(),
        public_end_of_service=PublicEndOfService.TFR_EMPLOYER,
        contribution_history=ContributionHistory(enrolled_on),
    )
    opening = PeriodState(
        accrual=EmploymentAccrualState(
            inps_bases=(InpsBaseYtd(2026, Decimal(121_500), Decimal(0)),)
        )
    )
    result = regular_period(
        employment=employment,
        employer=replace(EMPLOYER, public_life_insurance=True),
        current_year=employment_only(),
        month=11,
        opening_state=opening,
    )
    return {
        c.name: (c.base, c.amount) for c in result.contribution_breakdown.components
    }


def test_credit_and_asv_stop_at_the_massimale() -> None:
    """Enrolled in 2005: the massimale applies to every pension contribution."""
    components = _components(date(2005, 3, 1))

    assert components["ivs_employee"][0] == _HEADROOM
    assert components["credit_employee"] == (_HEADROOM, Decimal("2.78"))
    assert components["life_insurance_employee"] == (_HEADROOM, Decimal("0.21"))
    assert components["life_insurance_employer"] == (_HEADROOM, Decimal("0.74"))


def test_without_the_massimale_the_whole_base_counts() -> None:
    """Enrolled before 1996: no massimale, the credit is on the whole base."""
    components = _components(date(1990, 3, 1))

    assert components["credit_employee"][0] == Decimal("2227.99")
