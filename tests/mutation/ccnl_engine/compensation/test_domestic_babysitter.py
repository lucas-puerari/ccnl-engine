"""Domestic 2026 Table B, H and L: BS 737.39 + 97.06 + 30.27 = 864.72.

The signed CCNL minimum table on PDF page 59 (sha256
122ca6a72196a835976abac7fb988dc1502973941d52891a546512347fdc9dcf)
lists monthly BS pay of 737.39, the Table H monthly sitter payment of
97.06 for Table B workers, and the Table L monthly certification payment
of 30.27. Without certification the same month's cash gross is 834.45.
The caller attests both the under-six child and the certification conditions.
"""

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
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.inputs import ContributableHours, Permanent, WeeklyHours
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

_SLUG = "lavoro-domestico-convivente-orario-ridotto"
_ENGINE = PayrollEngine.bundled()


@pytest.mark.parametrize(
    ("certified", "gross", "codes"),
    [
        (False, "834.45", {"IND_BABYSITTER"}),
        (True, "864.72", {"IND_BABYSITTER", "IND_CERTIFICAZIONE_UNI"}),
    ],
)
def test_bs_sitter_month_with_optional_certification(
    certified: bool, gross: str, codes: set[str]
) -> None:
    """737.39 + 97.06 = 834.45; certification adds 30.27 = 864.72."""
    roles = {"baby_sitter_under_6"}
    if certified:
        roles.add("certificazione_uni_11766")
    result = _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 20),
            employment=Employment(
                ccnl_id=_SLUG,
                level_code="BS",
                seniority=new_hire(),
                weekly_hours=WeeklyHours(Decimal(30)),
                roles=frozenset(roles),
                contract_type=Permanent(),
            ),
            employer=EmployerProfile(headcount=Headcount(1)),
            facts=PeriodFacts(contributable_hours=ContributableHours(Decimal(130))),
        )
    )
    assert result.period_gross == Decimal(gross)
    assert {
        code for code in codes if any(code in i.item_id for i in result.pay_items)
    } == codes
    assert not any(
        "babysitter_and_certification_allowances" in x.id
        for x in result.assurance.limitations
    )


def test_allowances_are_level_local_and_require_attested_roles() -> None:
    """Only B and BS have Table L; only BS has Table H in Table B."""
    agreement = load_ccnl(_SLUG)
    for level, expected in (
        ("B", {"IND_CERTIFICAZIONE_UNI"}),
        ("BS", {"IND_BABYSITTER", "IND_CERTIFICAZIONE_UNI"}),
        ("C", set()),
    ):
        allowances = agreement.level_by_code(level).fixed_allowances
        assert {a.code for a in allowances if a.role is not None} == expected
