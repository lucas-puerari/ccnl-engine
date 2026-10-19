"""Model limitations: scope matching, triggers and blocking."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from typing import Any

import pytest
from pydantic import ValidationError

from ccnl_engine.limitation.models import (
    LimitationFacts,
    LimitationScope,
    LimitationStatus,
    ModelLimitation,
    MonetaryImpact,
)
from ccnl_engine.limitation.types import ResultTotal

_FACTS = LimitationFacts(
    ccnl_id="ccnl-a",
    as_of=date(2026, 6, 1),
    contract_type="apprentice",
    level_code="3",
    worker_category="impiegato",
    run_kind="regular",
    seniority_months=24,
    applicable=frozenset({"base_salary", "seniority"}),
    headcount=16,
)


def _limitation(**overrides: Any) -> ModelLimitation:  # noqa: ANN401
    fields: dict[str, Any] = {
        "id": "ccnl-a/variant",
        "capability": "base_salary",
        "variant": "variant",
        "summary": "what differs",
        "monetary_impact": MonetaryImpact.YES,
        "rulesets": ("ccnl-a",),
        "source": "ccnl/ccnl-a:coverage.notes",
        "remediation": "model it",
    }
    return ModelLimitation(**(fields | overrides))


@pytest.mark.parametrize(
    ("scope", "expected"),
    [
        ({}, True),
        ({"contract_types": ["apprentice"]}, True),
        ({"contract_types": ["permanent"]}, False),
        ({"levels": ["3", "4"]}, True),
        ({"levels": ["4"]}, False),
        ({"worker_categories": ["impiegato"]}, True),
        ({"worker_categories": ["operaio"]}, False),
        ({"run_kinds": ["fourteenth"]}, False),
        ({"run_kinds": ["regular"]}, True),
        ({"seniority_months_from": 24}, True),
        ({"seniority_months_from": 25}, False),
        ({"headcount_from": 16}, True),
        ({"headcount_from": 17}, False),
        ({"effective_from": "2026-06-01"}, True),
        ({"effective_from": "2026-06-02"}, False),
        ({"effective_until": "2026-06-02"}, True),
        ({"effective_until": "2026-06-01"}, False),
    ],
)
def test_scope_restrictions_match_the_facts(
    scope: dict[str, Any], expected: bool
) -> None:
    """Every restriction set must match; boundaries are from-inclusive."""
    assert LimitationScope.model_validate(scope).matches(_FACTS) is expected


def test_unknown_facts_never_rule_a_run_out() -> None:
    """An unknown category, seniority or headcount keeps the limitation."""
    facts = replace(_FACTS, worker_category=None, seniority_months=None, headcount=None)
    scope = LimitationScope.model_validate({
        "worker_categories": ["operaio"],
        "seniority_months_from": 120,
        "headcount_from": 16,
    })
    assert scope.matches(facts)


def test_scope_dates_must_be_ordered() -> None:
    """The end of a scope follows its start."""
    with pytest.raises(ValidationError, match="must follow"):
        LimitationScope.model_validate({
            "effective_from": "2026-06-01",
            "effective_until": "2026-06-01",
        })


def test_run_limitation_applies_to_its_rulesets_only() -> None:
    """A run limitation concerns the CCNLs it lists."""
    limitation = _limitation()
    assert limitation.applies_to(_FACTS)
    assert not limitation.applies_to(replace(_FACTS, ccnl_id="ccnl-b"))


def test_capability_must_concern_the_run() -> None:
    """A limitation of a capability the run does not apply is not recorded."""
    assert not _limitation(capability="overtime").applies_to(_FACTS)


def test_path_limitation_applies_when_traversed() -> None:
    """A path limitation needs the traversal, whatever the CCNL."""
    limitation = _limitation(
        id="engine_path",
        rulesets=("ccnl-b",),
        applies_when={"trigger": "path"},
    )
    assert not limitation.applies_to(_FACTS)
    assert limitation.applies_to(replace(_FACTS, traversed=frozenset({"engine_path"})))


def test_owed_limitation_applies_whatever_the_capability() -> None:
    """An amount owed in every run concerns the CCNL even off its capability."""
    limitation = _limitation(
        capability="bilateral_funds", applies_when={"trigger": "owed"}
    )
    assert limitation.applies_to(_FACTS)
    assert not limitation.applies_to(replace(_FACTS, ccnl_id="ccnl-b"))


def test_owed_limitation_keeps_its_scope() -> None:
    """An owed amount of the operai only does not concern an impiegato."""
    limitation = _limitation(
        applies_when={"trigger": "owed", "worker_categories": ["operaio"]}
    )
    assert not limitation.applies_to(_FACTS)


def test_limitation_totals_default_to_both() -> None:
    """A limitation touches both totals unless it names one."""
    assert _limitation().totals == frozenset(ResultTotal)
    employer = _limitation(totals=["employer_cost"])
    assert employer.totals == frozenset({ResultTotal.EMPLOYER_COST})


def test_limitation_names_at_least_one_total() -> None:
    """A limitation that touches no total is not a limitation."""
    with pytest.raises(ValidationError, match="at least 1"):
        _limitation(totals=[])


def test_outside_input_limitation_never_applies() -> None:
    """A limitation whose trigger has no request field is documented only."""
    limitation = _limitation(applies_when={"trigger": "outside_input"})
    assert not limitation.applies_to(_FACTS)


@pytest.mark.parametrize(
    ("impact", "status", "blocks"),
    [
        (MonetaryImpact.YES, LimitationStatus.OPEN, True),
        (MonetaryImpact.UNKNOWN, LimitationStatus.OPEN, True),
        (MonetaryImpact.NO, LimitationStatus.OPEN, False),
        (MonetaryImpact.YES, LimitationStatus.RESOLVED, False),
    ],
)
def test_open_monetary_limitations_block(
    impact: MonetaryImpact, status: LimitationStatus, blocks: bool
) -> None:
    """Only an open limitation that can move an amount blocks."""
    assert _limitation(monetary_impact=impact, status=status).blocks is blocks
