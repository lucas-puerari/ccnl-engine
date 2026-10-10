"""The assistance contribution of a CCNL rejects negative hourly rates."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from ccnl_engine.contract.fund.models_assistance import AssistanceContribution
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


def _contribution(employee: str, employer: str) -> AssistanceContribution:
    return AssistanceContribution(
        employee_per_hour=_series(employee),
        employer_per_hour=_series(employer),
        provenance=RuleProvenance(status=ProvenanceStatus.ASSUMED),
    )


def test_rates_are_read_per_hour() -> None:
    """Art. 54 c. 2 CCNL lavoro domestico: 0.02 worker, 0.04 employer.

    The period before 2021 is a gap: chiarimento a verbale 6 sets these
    rates from 1 January 2021.
    """
    contribution = _contribution("0.02", "0.04")

    day = date(2026, 3, 1)
    assert contribution.employee_per_hour.value_at(day) == Decimal("0.02")
    assert contribution.employer_per_hour.value_at(day) == Decimal("0.04")


@pytest.mark.parametrize(
    ("employee", "employer"), [("-0.02", "0.04"), ("0.02", "-0.04")]
)
def test_negative_rate_is_rejected(employee: str, employer: str) -> None:
    """A negative share is a data error."""
    with pytest.raises(ValidationError, match="must be >= 0"):
        _contribution(employee, employer)
