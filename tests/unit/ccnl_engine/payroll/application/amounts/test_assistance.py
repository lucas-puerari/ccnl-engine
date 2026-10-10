"""The assistance contribution of a run is charged per contributable hour.

CCNL lavoro domestico of 28 October 2025, art. 54 c. 2: 0.06 EUR per paid
hour, of which 0.02 charged to the worker, so 0.04 to the employer.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.errors import MissingRequiredFactError
from ccnl_engine.payroll.application.amounts._assistance import (
    AssistanceTerms,
    run_assistance,
)
from ccnl_engine.provenance.source.models_chain import ProvenanceStatus, RuleProvenance

_TERMS = AssistanceTerms(
    employee_per_hour=Decimal("0.02"),
    employer_per_hour=Decimal("0.04"),
    provenance=RuleProvenance(status=ProvenanceStatus.ASSUMED),
)


def test_no_contribution_without_terms() -> None:
    """A CCNL that charges no contribution charges nothing."""
    assert run_assistance(None, Decimal(216)) is None


def test_shares_on_the_contributable_hours() -> None:
    """216 hours: worker 216 x 0.02 = 4.32, employer 216 x 0.04 = 8.64."""
    contribution = run_assistance(_TERMS, Decimal(216))

    assert contribution is not None
    assert (contribution.employee, contribution.employer) == (
        Decimal("4.32"),
        Decimal("8.64"),
    )
    assert contribution.hours == Decimal(216)


def test_missing_hours_are_refused() -> None:
    """The contribution cannot be charged without the paid hours."""
    with pytest.raises(MissingRequiredFactError, match="contributable_hours"):
        run_assistance(_TERMS, None)
