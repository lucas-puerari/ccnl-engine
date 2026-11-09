"""Type specifications for the request's contract and employer inputs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.contribution.ceiling.inputs import ContributionHistory
from ccnl_engine.employer.inputs import EmployerProfile
from ccnl_engine.employment.inputs import Apprentice, FixedTerm, Permanent
from ccnl_engine.validators import FieldSpec

if TYPE_CHECKING:
    from ccnl_engine.period.requests import PeriodCalculationRequest


def contract_field_specs(request: PeriodCalculationRequest) -> tuple[FieldSpec, ...]:
    """Return type checks for the contract, employer and history fields.

    Returns:
        The contract-related field specifications of the request.
    """
    return (
        (
            "contract_type",
            request.contract_type,
            (Permanent, Apprentice, FixedTerm),
            False,
        ),
        ("employer", request.employer, EmployerProfile, False),
        (
            "contribution_history",
            request.contribution_history,
            ContributionHistory,
            True,
        ),
        ("events", request.events, (tuple, list), False),
    )
