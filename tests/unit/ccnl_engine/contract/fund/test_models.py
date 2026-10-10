"""The contractual fund contribution of a CCNL rejects negative amounts."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from ccnl_engine.contract.fund.models import ContractualFundContribution
from ccnl_engine.contract.identity.rules_validity import (
    SalaryGapKind,
    TimeSeries,
    ValidityPeriod,
)
from ccnl_engine.provenance.source.models_chain import ProvenanceStatus, RuleProvenance


def _series(value: str) -> TimeSeries:
    return TimeSeries(
        periods=(
            ValidityPeriod(
                gap_kind=SalaryGapKind.NOT_APPLICABLE,
                valid_from=date(2020, 1, 1),
                valid_until=date(2021, 1, 1),
            ),
            ValidityPeriod(
                value=Decimal(value), valid_from=date(2021, 1, 1), valid_until=None
            ),
        )
    )


def _contribution(value: str) -> ContractualFundContribution:
    return ContractualFundContribution(
        code="FONDAPI",
        description="Fondapi",
        monthly_by_level={"5": _series(value)},
        provenance=RuleProvenance(status=ProvenanceStatus.ASSUMED),
    )


def test_amount_and_gap_accepted() -> None:
    """A gap period and a non-negative amount are valid."""
    assert _contribution("6.80").monthly_by_level["5"].value_at(
        date(2026, 1, 1)
    ) == Decimal("6.80")


def test_negative_amount_rejected() -> None:
    """A negative monthly amount is a data-entry error."""
    with pytest.raises(ValidationError, match=r"monthly_by_level\[5\] must be >= 0"):
        _contribution("-1")
