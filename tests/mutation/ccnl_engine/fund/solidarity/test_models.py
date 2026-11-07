"""A solidarity fund on top of the sector rates, or by headcount in place of the FIS.

D.I. 21 May 2024 art. 6 c. 1: the Fondo delle attività professionali
charges 0.50% up to 5, 0.80% up to 15 and 1% above 15 employees, two thirds
employer, in place of the FIS and the CIGS of the terziario rates.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from pydantic import ValidationError

from ccnl_engine.contribution.rate.models import ApprenticeRates, InpsRates
from ccnl_engine.fund.solidarity.models import (
    SolidarityFund,
    SolidarityTier,
    with_solidarity_tiers,
)
from ccnl_engine.provenance.source.models import (
    SourceDocument,
    SourceKind,
    SourceLocation,
)
from ccnl_engine.provenance.source.rule.models import ProvenanceStatus, RuleProvenance

if TYPE_CHECKING:
    from ccnl_engine.sector.models import YearRules

_PROVENANCE = RuleProvenance(
    status=ProvenanceStatus.DERIVED,
    location=SourceLocation(
        source_document=SourceDocument(
            document_id="di-21-05-2024-attivita-professionali",
            title="D.I. 21 maggio 2024",
            kind=SourceKind.AMMINISTRAZIONE,
        ),
    ),
)
_TIERS = (
    SolidarityTier(
        max_employees=15,
        employer_rate=Decimal("0.0053333"),
        employee_rate=Decimal("0.0026667"),
    ),
    SolidarityTier(
        max_employees=5,
        employer_rate=Decimal("0.0033333"),
        employee_rate=Decimal("0.0016667"),
    ),
    SolidarityTier(
        employer_rate=Decimal("0.0066667"), employee_rate=Decimal("0.0033333")
    ),
)
_FUND = SolidarityFund(
    code="FSAP", wage_integration_tiers=_TIERS, provenance=_PROVENANCE
)


@pytest.mark.parametrize(
    ("headcount", "employer"),
    [(3, "0.0033333"), (5, "0.0033333"), (6, "0.0053333"), (16, "0.0066667")],
)
def test_the_tier_of_the_headcount(headcount: int, employer: str) -> None:
    """The narrowest tier that covers the headcount, else the open one."""
    assert _FUND.tier(headcount).employer_rate == Decimal(employer)


@pytest.mark.parametrize(
    "fields",
    [
        {"employer_rate": Decimal("0.001")},
        {},
        {
            "employer_rate": Decimal("0.001"),
            "employee_rate": Decimal("0.001"),
            "wage_integration_tiers": _TIERS,
        },
        {"wage_integration_tiers": _TIERS[:2]},
        {"wage_integration_tiers": (_TIERS[2], _TIERS[2])},
    ],
)
def test_a_fund_has_one_shape(fields: dict[str, object]) -> None:
    """Both flat rates, or tiers with exactly one open tier."""
    with pytest.raises(ValidationError):
        SolidarityFund.model_validate({
            "code": "X",
            "provenance": _PROVENANCE,
            **fields,
        })


def _inps() -> InpsRates:
    return InpsRates(
        employee_rate=Decimal("0.0975667"),
        employee_ivs_rate=Decimal("0.0919"),
        employer_rate=Decimal("0.3011333"),
        employer_ivs_rate=Decimal("0.2381"),
        ceiling=None,
        wage_integration_employer_rate=Decimal("0.0113333"),
        wage_integration_employee_rate=Decimal("0.0056667"),
        employer_rate_by_category={},
    )


def _apprentice() -> ApprenticeRates:
    return ApprenticeRates(
        employee_rate=Decimal("0.0640667"),
        employee_ivs_rate=Decimal("0.0584"),
        employer_rate_months_0_11=Decimal("0.1274333"),
        employer_ivs_rate_months_0_11=Decimal("0.1000"),
        employer_rate_months_12_23=Decimal("0.1274333"),
        employer_ivs_rate_months_12_23=Decimal("0.1000"),
        employer_rate_after=Decimal("0.1274333"),
        employer_ivs_rate_after=Decimal("0.1000"),
    )


class _Rules:
    """The two fields of the year rules the swap reads and copies."""

    def __init__(
        self, inps: InpsRates | None, apprentice: ApprenticeRates | None
    ) -> None:
        self.inps = inps
        self.apprentice = apprentice

    def model_copy(self, *, update: dict[str, object]) -> _Rules:
        return _Rules(
            update.get("inps", self.inps),  # type: ignore[arg-type]
            update.get("apprentice", self.apprentice),  # type: ignore[arg-type]
        )


def test_the_tier_replaces_the_wage_integration_shares() -> None:
    """Above 15: 1.13333/0.56667 out, 0.66667/0.33333 in, apprentices too."""
    rules: YearRules = _Rules(_inps(), _apprentice())  # type: ignore[assignment]
    swapped = with_solidarity_tiers(rules, _FUND, 60)

    assert swapped.inps is not None
    assert swapped.inps.employer_rate == Decimal("0.2964667")
    assert swapped.inps.employee_rate == Decimal("0.0952333")
    assert swapped.apprentice is not None
    assert swapped.apprentice.employer_rate_after == Decimal("0.1227667")
    assert swapped.apprentice.employee_rate == Decimal("0.0617333")


def test_rules_without_apprentice_rates_keep_none() -> None:
    """A sector with no apprentice block swaps the ordinary rates only."""
    rules: YearRules = _Rules(_inps(), None)  # type: ignore[assignment]
    assert with_solidarity_tiers(rules, _FUND, 60).apprentice is None


@pytest.mark.parametrize(
    ("inps", "fund"),
    [
        (None, _FUND),
        (_inps(), None),
        (
            _inps(),
            SolidarityFund(
                code="FLAT",
                employer_rate=Decimal("0.00133"),
                employee_rate=Decimal("0.00067"),
                provenance=_PROVENANCE,
            ),
        ),
    ],
)
def test_no_swap_without_a_tiered_fund_or_inps_rates(
    inps: InpsRates | None, fund: SolidarityFund | None
) -> None:
    """A flat fund, no fund or a domestic sector leave the rules as they are."""
    rules: YearRules = _Rules(inps, None)  # type: ignore[assignment]
    assert with_solidarity_tiers(rules, fund, 60) is rules
