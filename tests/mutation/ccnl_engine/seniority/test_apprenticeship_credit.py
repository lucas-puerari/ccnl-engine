"""A retained apprentice reaches the first increment on fractional credit.

For a 36-month apprenticeship, 36 * 0.65 = 23.4 months. At retention
on 1 January 2025 the increment is EUR 0; after one completed month,
23.4 + 1 = 24.4 >= 24, so February pays one level-2 increment of
EUR 21.59. With no credit the first increment would pay in January 2027.
The production agreement is left unchanged: the rule is copied in memory.
"""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.element.services import _resolve_chain
from ccnl_engine.decision.models import CalculationStatus
from ccnl_engine.employment.inputs import Apprentice, Permanent
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.seniority.credit import credited_increment_months
from ccnl_engine.seniority.inputs import SeniorityFact, SenioritySource
from ccnl_engine.seniority.services import run_seniority

if TYPE_CHECKING:
    from ccnl_engine.period.context.services import RunContext

_ORIGINAL = load_ccnl("metalmeccanico-confapi")
_RULES = _ORIGINAL.parameters.seniority_increments.model_copy(
    update={"apprenticeship_credit_share": Decimal("0.65")}
)
_CCNL = _ORIGINAL.model_copy(
    update={
        "parameters": _ORIGINAL.parameters.model_copy(
            update={"seniority_increments": _RULES}
        )
    }
)
_RETENTION = date(2025, 1, 1)


def _request(duration: int | None) -> PeriodCalculationRequest:
    fact = SeniorityFact(
        0,
        _RETENTION,
        SenioritySource.EMPLOYER_RECORDS,
        apprenticeship_months=duration,
    )
    return cast(
        "PeriodCalculationRequest",
        SimpleNamespace(seniority=fact, contract_type=Permanent(), roles=frozenset()),
    )


def _amount(day: date, duration: int | None) -> Decimal:
    request = _request(duration)
    months = request.seniority.months_in_month(day.year, day.month)  # type: ignore[union-attr]
    credited = credited_increment_months(months, _RULES, request)
    chain, _ = _resolve_chain(
        _CCNL,
        _CCNL.level_by_code("2"),
        Permanent(),
        day,
        seniority_months=months,
        increment_months=-1 if credited is None else credited,
    )
    return chain.seniority


def test_fractional_credit_moves_first_increment_to_february() -> None:
    """EUR 0 in January and EUR 21.59 in February; no credit delays two years."""
    assert _amount(_RETENTION, 36) == Decimal(0)
    assert _amount(date(2025, 2, 1), 36) == Decimal("21.59")
    assert _amount(date(2025, 2, 1), 0) == Decimal(0)
    assert _amount(date(2027, 1, 1), 0) == Decimal("21.59")


def test_unknown_duration_blocks_and_apprentices_do_not_get_credit() -> None:
    """An absent duration counts the service alone and names the fact.

    Current apprentices have no credited step.
    """
    request = _request(None)
    assert credited_increment_months(1, _RULES, request) == 1
    ctx = cast(
        "RunContext",
        SimpleNamespace(
            contract=SimpleNamespace(
                ccnl=_CCNL,
                level=_CCNL.level_by_code("2"),
                tctx=SimpleNamespace(competence=date(2025, 2, 1)),
            ),
            request=request,
            worker_category=None,
            chain=SimpleNamespace(seniority=Decimal(0)),
        ),
    )
    run = run_seniority(ctx)
    assert not run.missing
    assert run.apprenticeship_missing
    issue = run.issue()
    assert issue is not None
    assert issue.fact == "apprenticeship_months"
    assert issue.status is CalculationStatus.INCOMPLETE
    assert run.months == 1
    apprentice = cast(
        "PeriodCalculationRequest",
        SimpleNamespace(seniority=request.seniority, contract_type=Apprentice(1)),
    )
    assert credited_increment_months(1, _RULES, apprentice) == 1
