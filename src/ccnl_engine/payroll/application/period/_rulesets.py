"""Rulesets the payable rules of a run were read from.

A rule identifier starts with the id of its ruleset (see
:mod:`~ccnl_engine.payroll.application.period._rule_lookup`); a ruleset is
reported when at least one rule an executed capability read names it.  A
ruleset without an identity record cannot be reported.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from ccnl_engine.payroll.application.period._context import RunContext
    from ccnl_engine.payroll.application.period._rule_sources import RuleSource
    from ccnl_engine.provenance.domain.ruleset_identity import RulesetIdentity

_SURTAX = frozenset({"addizionale_regionale", "addizionale_comunale"})


def _candidates(
    ctx: RunContext, capabilities: frozenset[str]
) -> Iterator[RulesetIdentity | None]:
    rules = ctx.contract.year_rules
    yield ctx.contract.ccnl.ruleset
    yield rules.ruleset
    yield rules.inps_ruleset
    yield ctx.var_pay_rules.ruleset
    if "family_deductions" in capabilities:
        yield ctx.repo.load_family_deduction_rules(ctx.fiscal_year).ruleset
    surtax = (
        ctx.repo.load_surtax_rules(ctx.fiscal_year) if capabilities & _SURTAX else None
    )
    if surtax is not None:
        yield surtax.regional_ruleset
        yield surtax.municipal_ruleset


def run_rulesets(
    ctx: RunContext, sources: Iterable[RuleSource]
) -> tuple[RulesetIdentity, ...]:
    """Return the identities of the rulesets the run read rules from.

    Args:
        ctx: Context of the run.
        sources: Provenance of every payable rule the run read.

    Returns:
        One identity per ruleset read, sorted by id.
    """
    sources = tuple(sources)
    read = {source.rule.partition(":")[0] for source in sources}
    capabilities = frozenset(source.capability for source in sources)
    found: dict[str, RulesetIdentity] = {}
    for ruleset in _candidates(ctx, capabilities):
        if ruleset is not None and ruleset.id in read:
            found.setdefault(ruleset.id, ruleset)
    return tuple(found[key] for key in sorted(found))
