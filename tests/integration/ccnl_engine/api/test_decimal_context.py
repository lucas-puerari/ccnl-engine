"""Results do not depend on the caller's decimal context.

A host may lower the precision or change the rounding of its thread
context for its own reasons; the engine computes in a fixed context, so the
same request returns the same amounts.
"""

from __future__ import annotations

import ast
from datetime import date
from decimal import ROUND_DOWN, Context, Decimal, localcontext
from pathlib import Path

from ccnl_engine import (
    CompetenceYearPlan,
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PeriodFacts,
)
from ccnl_engine.inputs import (
    ContributableHours,
    EmploymentPeriod,
    FamilyComposition,
    Permanent,
    SeniorityFact,
    SenioritySource,
    WeeklyHours,
)

_HIRED = date(2026, 1, 1)
_SOURCE_DIR = Path(__file__).parents[4] / "src" / "ccnl_engine"


def _plan(
    ccnl_id: str, level_code: str, hours: ContributableHours | None
) -> CompetenceYearPlan:
    return CompetenceYearPlan(
        year=2026,
        employment=Employment(
            ccnl_id=ccnl_id,
            level_code=level_code,
            contract_type=Permanent(),
            employment_period=EmploymentPeriod(_HIRED, None),
            seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
            weekly_hours=WeeklyHours(25),
        ),
        employer=EmployerProfile(headcount=Headcount(60)),
        default_facts=PeriodFacts(
            regione="IT-25",
            comune_belfiore="F205",
            family_composition=FamilyComposition(),
            contributable_hours=hours,
        ),
    )


def test_hostile_context_changes_no_amount() -> None:
    """A part-time year under a 6-digit, round-down context equals the default."""
    engine = PayrollEngine.bundled()
    for ccnl_id, level, hours in (
        ("chimica-farmaceutica-federchimica", "D1", None),
        ("lavoro-domestico-non-convivente", "B", ContributableHours(Decimal(108))),
    ):
        plan = _plan(ccnl_id, level, hours)
        expected = engine.calculate_competence_year(plan)
        with localcontext(Context(prec=6, rounding=ROUND_DOWN)):
            hostile = engine.calculate_competence_year(plan)
        assert hostile == expected
        assert hostile.annual_net == expected.annual_net


def test_every_quantize_states_its_rounding() -> None:
    """No ``quantize`` in the package falls back on the context rounding.

    The fixed context covers the facade; a ``quantize`` reached from an input
    constructor or a loader runs in the caller's context instead.
    """
    bare = [
        f"{path.relative_to(_SOURCE_DIR)}:{node.lineno}"
        for path in sorted(_SOURCE_DIR.rglob("*.py"))
        for node in ast.walk(ast.parse(path.read_text("utf-8")))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "quantize"
        and len(node.args) < 2
        and not any(keyword.arg == "rounding" for keyword in node.keywords)
    ]
    assert bare == []
