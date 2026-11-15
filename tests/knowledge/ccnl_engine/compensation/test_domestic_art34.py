"""The allowances of art. 34 of the domestic CCNL and the worker's superminimi.

Art. 34 c. 3: the baby sitter allowance (Tabella H, 138.54 in 2026) "è
assorbibile da eventuali superminimi individuali di miglior favore"; c. 5
keeps whole a treatment "ad personam non assorbibile".  C. 7: the UNI
certification allowance (Tabella L, 30.27) "è assorbibile da eventuali
trattamenti retributivi di miglior favore complessivamente percepiti".
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.compensation.allowance.models import Allowance
from ccnl_engine.inputs import (
    ContributableHours,
    IndividualElement,
    Permanent,
    WeeklyHours,
)

_ENGINE = PayrollEngine.bundled()


def _allowances(role: str, *elements: IndividualElement) -> dict[str, Decimal]:
    result = _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id="lavoro-domestico-convivente",
                level_code="BS",
                weekly_hours=WeeklyHours(Decimal(54)),
                contract_type=Permanent(),
                roles=frozenset({role}),
                individual_elements=elements,
            ),
            employer=EmployerProfile(headcount=Headcount(1)),
            facts=PeriodFacts(contributable_hours=ContributableHours(Decimal(234))),
        )
    )
    return {
        i.allowance_code: i.amount
        for i in result.pay_items
        if i.kind == "fixed_allowance_earning" and i.allowance_code
    }


def _superminimo(absorbable: bool) -> IndividualElement:
    return IndividualElement(
        "superminimo",
        Decimal(50),
        absorbable=absorbable,
        as_of=date(2026, 1, 1) if absorbable else None,
    )


@pytest.mark.parametrize(
    ("absorbable", "babysitter"), [(True, "88.54"), (False, "138.54")]
)
def test_only_an_absorbable_superminimo_absorbs_the_babysitter_allowance(
    absorbable: bool,
    babysitter: str,
) -> None:
    """50 of absorbable superminimo leave 88.54; ad personam, 138.54."""
    paid = _allowances("baby_sitter_under_6", _superminimo(absorbable))
    assert paid["IND_BABYSITTER"] == Decimal(babysitter)
    assert paid["superminimo"] == Decimal(50)


def test_any_better_treatment_absorbs_the_certification_allowance() -> None:
    """C. 7: even a superminimo ad personam absorbs the 30.27."""
    paid = _allowances("certificazione_uni_11766", _superminimo(False))
    assert paid.get("IND_CERTIFICAZIONE_UNI", Decimal(0)) == 0


def test_without_individual_elements_the_allowance_is_whole() -> None:
    """No superminimo: the whole 138.54."""
    assert _allowances("baby_sitter_under_6")["IND_BABYSITTER"] == Decimal("138.54")


def test_absorbable_only_needs_the_absorption() -> None:
    """The restriction to absorbable elements is of an absorbed allowance."""
    series = {
        "periods": [{"valid_from": "2026-01-01", "valid_until": None, "value": "1"}]
    }
    with pytest.raises(ValidationError, match="needs absorption"):
        Allowance.model_validate({
            "code": "X",
            "description": "x",
            "monthly": series,
            "absorbed_by_absorbable_only": True,
        })
