"""The indennità di cassa of DMO and Terziario Confesercenti, by role.

DMO Testo Unico of 29 September 2025, Art. 202 (p. 59, sha256
9bb56adb31c2f6aa2c65c48dbe60774701367658177dd544391ccf2da70fbbaf), and
Terziario Confesercenti, Art. 218 (p. 158, sha256
18a2f10cf41209a56523473660321348214c1d8d54900257cf805ad8488f7ec0): "al
personale normalmente adibito ad operazioni di cassa con carattere di
continuità [...] compete un'indennità di cassa e di maneggio di denaro nella
misura del 5% (cinque per cento) della paga base nazionale conglobata".

Level IV, January 2026: paga base 1,257.46 in both texts (DMO Art. 196:
1,122.46 + 70 + 30 + 35 from 1 November 2025; Terziario: the total 1,781.68
less the contingenza 524.22), so 62.873 rounds to 62.87.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.inputs import EmploymentPeriod, Permanent, WorkerCategory
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

_ENGINE = PayrollEngine.bundled()


def _cassa(slug: str, roles: frozenset[str]) -> list[Decimal]:
    result = _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 27),
            employment=Employment(
                ccnl_id=slug,
                level_code="IV",
                category=WorkerCategory.IMPIEGATO,
                seniority=new_hire(),
                roles=roles,
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(date(2026, 1, 1)),
            ),
            employer=EmployerProfile(headcount=Headcount(20)),
            facts=PeriodFacts(regione="IT-25", comune_belfiore="A005"),
        )
    )
    assert not [b for b in result.blockers if "roles" in b.detail]
    return [i.amount for i in result.pay_items if "IND_CASSA" in i.item_id]


@pytest.mark.parametrize("slug", ["dmo-federdistribuzione", "terziario-confesercenti"])
def test_the_cashier_is_paid_five_percent_of_the_paga_base(slug: str) -> None:
    """62.87 to the cassiere, nothing to a worker who holds no role."""
    assert _cassa(slug, frozenset({"cassiere"})) == [Decimal("62.87")]
    assert _cassa(slug, frozenset()) == []
