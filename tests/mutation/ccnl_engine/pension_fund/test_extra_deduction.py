"""The extra deduction of D.Lgs. 252/2005 art. 8 c. 6, stated by the worker.

A worker first employed after 2006 deducts, past the fifth year of
membership, more than the annual cap; the withholding agent applies it
(AdE circ. 70/E/2007), so the enrolment states it.  Contributions above
the cap left with none stated carry the missing fact ``extra_deduction``.
"""

from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.pension_fund.inputs import PensionFundEnrolment
from ccnl_engine.pension_fund.rules import PensionContribution, _contribution
from ccnl_engine.pension_fund.services import (
    EXTRA_DEDUCTION_UNKNOWN,
    extra_deduction_issue,
)

if TYPE_CHECKING:
    from ccnl_engine.pension_fund.models import ComplementaryPensionRules
    from ccnl_engine.pension_fund.rules import PensionFundTerms

_RULES = cast(
    "ComplementaryPensionRules",
    SimpleNamespace(deduction_cap=Decimal("5164.57"), solidarity_rate=Decimal("0.10")),
)


def _terms(extra: Decimal | None) -> PensionFundTerms:
    return cast("PensionFundTerms", SimpleNamespace(extra_deduction=extra))


def _paid(deductible: str, extra: Decimal | None = None) -> PensionContribution:
    return PensionContribution(
        terms=_terms(extra),
        base=Decimal(0),
        employer=Decimal("60.00"),
        employee=Decimal("40.00"),
        solidarity=Decimal("6.00"),
        deductible=Decimal(deductible),
        contractual=Decimal(0),
    )


def test_the_stated_extra_raises_the_cap_left() -> None:
    """5,164.57 already deducted: 100 more only with 2,582.29 stated."""
    deducted = Decimal("5164.57")
    amounts = (Decimal(60), Decimal(40), Decimal(0))

    plain = _contribution(_terms(None), _RULES, Decimal(0), amounts, deducted)
    extra = _contribution(
        _terms(Decimal("2582.29")), _RULES, Decimal(0), amounts, deducted
    )
    alone = _contribution(None, _RULES, Decimal(0), amounts, deducted)

    assert (plain.deductible, extra.deductible, alone.deductible) == (
        Decimal(0),
        Decimal(100),
        Decimal(0),
    )


@pytest.mark.parametrize(
    ("deductible", "extra", "issue"),
    [
        ("100.00", None, None),
        ("99.99", None, EXTRA_DEDUCTION_UNKNOWN),
        ("99.99", Decimal(0), None),
    ],
)
def test_only_a_capped_run_without_the_fact_names_it(
    deductible: str, extra: Decimal | None, issue: object
) -> None:
    """All deducted: nothing; one cent short and unstated: the missing fact."""
    assert extra_deduction_issue(_paid(deductible, extra)) is issue


def test_no_enrolment_names_nothing() -> None:
    """A worker not enrolled, or contractual contributions only."""
    alone = PensionContribution(
        terms=None,
        base=Decimal(0),
        employer=Decimal("60.00"),
        employee=Decimal(0),
        solidarity=Decimal(0),
        deductible=Decimal(0),
        contractual=Decimal("60.00"),
    )

    assert extra_deduction_issue(None) is None
    assert extra_deduction_issue(alone) is None
    assert EXTRA_DEDUCTION_UNKNOWN.fact == "extra_deduction"


def test_the_extra_cannot_be_negative() -> None:
    """A deduction is at least zero."""
    with pytest.raises(InvalidInputError, match="extra_deduction"):
        PensionFundEnrolment(
            "ALIFOND", Decimal("0.01"), True, extra_deduction=Decimal(-1)
        )
