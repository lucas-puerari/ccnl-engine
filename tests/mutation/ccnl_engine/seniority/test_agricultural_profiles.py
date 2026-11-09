"""Post-2006 provincial professional-profile scatti of Art. 54, PDF pp. 55-56."""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

import pytest

from ccnl_engine.agreement.validators import _check_category_level_codes
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.comparison.ruleset.rules import _seniority_rules
from ccnl_engine.compensation.element.rules import _level_chain
from ccnl_engine.compensation.element.services import _resolve_chain
from ccnl_engine.employment.fact.roles import roles_issue
from ccnl_engine.employment.inputs import FixedTerm, Permanent
from ccnl_engine.seniority.rules import _resolve_seniority_count

if TYPE_CHECKING:
    from ccnl_engine.period.context.services import RunContext

_CCNL = load_ccnl("operai-agricoli-florovivaisti")
_AS_OF = date(2026, 7, 1)


@pytest.mark.parametrize(
    ("contract_type", "expected"),
    [(FixedTerm(), "0"), (Permanent(), "23.86")],
)
def test_permanent_only_scatti_at_48_months(
    contract_type: FixedTerm | Permanent, expected: str
) -> None:
    """At 48 months Area 2 super pays 2 x 11.93 = 23.86 only to permanent workers."""
    chain, _ = _resolve_chain(
        _CCNL,
        _CCNL.level_by_code("Area2"),
        contract_type,
        _AS_OF,
        seniority_months=48,
        roles=frozenset({"qualified_super"}),
        worker_category=None,
        hired_on=date(2022, 6, 1),
    )
    assert chain.seniority == Decimal(expected)


@pytest.mark.parametrize(
    ("level", "role", "step", "first", "second"),
    [
        ("Area2", "qualified_super", "11.93", "11.93", "23.86"),
        ("Area1", "specialized_super", "12.78", "12.78", "25.56"),
    ],
)
def test_two_profile_steps_by_service_months(
    level: str, role: str, step: str, first: str, second: str
) -> None:
    """24 and 48 months pay 1 and 2 steps: 2 x 11.93 = 23.86; 2 x 12.78 = 25.56."""
    rules = _CCNL.parameters.seniority_increments
    assert rules.amount_by_level_by_role[role][level].value_at(_AS_OF) == Decimal(step)
    for months, expected in ((23, "0"), (24, first), (47, first), (48, second)):
        count = _resolve_seniority_count(rules, level, None, months)
        chain = _level_chain(
            _CCNL,
            _CCNL.level_by_code(level),
            count,
            frozenset({role}),
            _AS_OF,
            is_apprentice=False,
        )
        assert chain.seniority == Decimal(expected)


@pytest.mark.parametrize(
    ("level", "step"),
    [("Area3", "9.89"), ("Area2", "11.36"), ("Area1", "12.50")],
)
def test_post_2006_base_profile_is_not_the_1983_amount(level: str, step: str) -> None:
    """For 48 months, the national profile baseline pays 2 x its post-2006 step."""
    chain = _level_chain(
        _CCNL,
        _CCNL.level_by_code(level),
        _resolve_seniority_count(
            _CCNL.parameters.seniority_increments, level, None, 48
        ),
        frozenset(),
        _AS_OF,
        is_apprentice=False,
    )
    assert chain.seniority == Decimal(step) * 2


def test_profile_rules_are_compared_and_reject_unknown_level() -> None:
    """A role series needs a known level and stays visible to rule comparison."""
    rules = _CCNL.parameters.seniority_increments
    compared = list(_seniority_rules(rules))
    assert any(
        "amount_by_level_by_role[qualified_super][Area2]" in rule.path
        for rule in compared
    )
    invalid = rules.model_copy(
        update={
            "amount_by_level_by_role": {
                "qualified_super": {
                    "missing": next(iter(rules.amount_by_level.values()))
                }
            }
        }
    )
    with pytest.raises(ValueError, match="references level code 'missing'"):
        _check_category_level_codes({"Area1", "Area2", "Area3"}, invalid)


def test_unknown_profile_is_needed_only_after_a_step_can_pay() -> None:
    """At 23 months no step pays; at 24 months the profile affects 11.36 vs 11.93."""
    level = _CCNL.level_by_code("Area2")
    for count, needs_role in ((0, False), (1, True)):
        chain = _level_chain(
            _CCNL, level, count, frozenset(), _AS_OF, is_apprentice=False
        )
        ctx = cast(
            "RunContext",
            SimpleNamespace(
                request=SimpleNamespace(roles=None),
                contract=SimpleNamespace(
                    ccnl=_CCNL,
                    level=level,
                    tctx=SimpleNamespace(competence=_AS_OF),
                ),
                chain=chain,
            ),
        )
        issue = roles_issue(ctx)
        assert (issue is not None) is needs_role
        if issue is not None:
            assert issue.fact == "roles"
