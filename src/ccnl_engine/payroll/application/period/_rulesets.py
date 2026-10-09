"""Rulesets a run read, with their identity, readiness and confidence.

The CCNL ruleset is always reported: its levels, divisor and extra months
shape every run.  Any other ruleset is reported when at least one payable
rule an executed capability read names it; a rule identifier starts with the
id of its ruleset (see
:mod:`~ccnl_engine.payroll.application.period._rule_lookup`).  The kind of
each ruleset is set by the loader that yielded it, never inferred from its
id.  A ruleset without an identity record cannot be reported.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.contract.domain.ruleset_readiness import ccnl_ruleset_assurance
from ccnl_engine.provenance.domain.ruleset_assurance import (
    RulesetAssurance,
    RulesetKind,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from ccnl_engine.payroll.application.period._context import RunContext
    from ccnl_engine.payroll.application.period._rule_sources import RuleSource
    from ccnl_engine.provenance.domain.ruleset_identity import RulesetIdentity

_SURTAX = frozenset({"addizionale_regionale", "addizionale_comunale"})
#: Engine limitation of a run that reads provisional tax rules.
PROVISIONAL_RULESET = "provisional_ruleset"
#: Engine limitation of a run that reads provisional INPS rules.
PROVISIONAL_INPS_RULESET = "provisional_inps_ruleset"


def provisional_paths(ctx: RunContext) -> frozenset[str]:
    """Return the limitation paths of a run on provisional tax or INPS rules.

    The IRPEF rules are those of the tax year of the payment, the INPS
    rules those of the competence year: either can be provisional.  Each
    has its own limitation, so a run that withholds no IRPEF (a household
    employer) still records the INPS one.  The other rulesets of a year
    (family deductions, somma esente, surtax) are provisional together
    with its tax ruleset.

    Returns:
        ``provisional_ruleset`` when the tax ruleset of the run is
        provisional, ``provisional_inps_ruleset`` when its INPS ruleset is.
    """
    rules = ctx.contract.year_rules
    paths = (
        (rules.ruleset, PROVISIONAL_RULESET),
        (rules.inps_ruleset, PROVISIONAL_INPS_RULESET),
    )
    return frozenset(
        path
        for identity, path in paths
        if identity is not None and identity.provisional
    )


def _candidates(
    ctx: RunContext, capabilities: frozenset[str]
) -> Iterator[tuple[RulesetKind, RulesetIdentity | None]]:
    rules = ctx.contract.year_rules
    yield RulesetKind.TAX, rules.ruleset
    yield RulesetKind.INPS, rules.inps_ruleset
    yield RulesetKind.TAX, ctx.var_pay_rules.ruleset
    if rules.tfr_revaluation is not None:
        yield RulesetKind.TAX, rules.tfr_revaluation.ruleset
    if rules.somma_esente is not None:
        yield RulesetKind.TAX, rules.somma_esente.ruleset
    if "family_deductions" in capabilities:
        family = ctx.repo.load_family_deduction_rules(ctx.fiscal_year)
        yield RulesetKind.TAX, family.ruleset
    surtax = (
        ctx.repo.load_surtax_rules(ctx.fiscal_year) if capabilities & _SURTAX else None
    )
    if surtax is not None:
        yield RulesetKind.SURTAX, surtax.regional_ruleset
        yield RulesetKind.SURTAX, surtax.municipal_ruleset


def run_rulesets(
    ctx: RunContext, sources: Iterable[RuleSource]
) -> tuple[RulesetAssurance, ...]:
    """Return the assurance of the rulesets the run read rules from.

    Args:
        ctx: Context of the run.
        sources: Provenance of every payable rule the run read.

    Returns:
        The CCNL ruleset, when it has an identity, and one assurance per
        other ruleset read, sorted by id.
    """
    sources = tuple(sources)
    read = {source.rule.partition(":")[0] for source in sources}
    capabilities = frozenset(source.capability for source in sources)
    found: dict[str, RulesetAssurance] = {}
    ccnl = ccnl_ruleset_assurance(ctx.contract.ccnl)
    if ccnl is not None:
        found[ccnl.id] = ccnl
    for kind, identity in _candidates(ctx, capabilities):
        if identity is not None and identity.id in read:
            found.setdefault(identity.id, RulesetAssurance.without_tier(identity, kind))
    return tuple(found[key] for key in sorted(found))
