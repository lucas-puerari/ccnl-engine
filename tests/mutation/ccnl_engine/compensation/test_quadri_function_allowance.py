"""The indennità di funzione of the quadri of the agenti immobiliari, by role.

CCNL agenti immobiliari FIAIP of 19 May 2025, Art. 162 note (*) (p. 97,
sha256 560d16410d3e41dc0bfb00bfe2a40ef65f2cd900234aeaee92018ed9fa21ead5):
"Ai quadri dipendenti da imprese di mediazione, nei casi di responsabilità
di unità operative o di unità locali, è riconosciuta una indennità di
funzione di € 250,00 mensili per 12 mensilità": paid on the monthly runs,
not on the extra months.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.inputs import EmploymentPeriod, Permanent
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

_ENGINE = PayrollEngine.bundled()
_ROLE = frozenset({"responsabile_unita"})


def _funzione(run: PayrollRun, roles: frozenset[str]) -> list[Decimal]:
    result = _ENGINE.calculate_period(
        PeriodInput(
            run=run,
            payment_date=date(2026, run.month, 20),
            employment=Employment(
                ccnl_id="agenti-immobiliari-fiaip",
                level_code="Q",
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
    return [i.amount for i in result.pay_items if "IND_FUNZIONE" in i.item_id]


def test_a_quadro_responsible_for_a_unit_is_paid_250_a_month() -> None:
    """250.00 on a monthly run; nothing without the role."""
    march = PayrollRun.regular(year=2026, month=3)
    assert _funzione(march, _ROLE) == [Decimal("250.00")]
    assert _funzione(march, frozenset()) == []


def test_the_allowance_has_no_share_in_the_extra_months() -> None:
    """12 mensilità: the tredicesima pays none of it."""
    assert _funzione(PayrollRun.thirteenth(year=2026, payment_month=12), _ROLE) == []


def test_the_quadri_of_the_consorzi_di_bonifica_take_140() -> None:
    """Consorzi di bonifica, Art. 78 (FLAI-CGIL text, p. 83, sha256 558ceea9...).

    "un'indennità di funzione in misura fissa pari ad Euro 140,00, da
    corrispondere per quattordici mensilità" to every quadro: the Area
    Quadri levels AQ162, AQ164, AQ185 and AQ187 (p. 11), no other level.
    """
    ccnl = load_ccnl("consorzi-di-bonifica-snebi")
    day = date(2026, 3, 1)
    paid = {
        level.code: [
            a.monthly.value_at(day)
            for a in level.fixed_allowances
            if a.code == "IND_FUNZIONE_QUADRI"
        ]
        for level in ccnl.levels
    }
    assert {code for code, amounts in paid.items() if amounts} == {
        "AQ162",
        "AQ164",
        "AQ185",
        "AQ187",
    }
    assert all(amounts == [Decimal("140.00")] for amounts in paid.values() if amounts)
