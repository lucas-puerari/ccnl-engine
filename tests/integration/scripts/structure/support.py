"""Tiers of the concepts of ``ccnl_engine`` and the imports across them.

A concept is a root directory of the package (``sickness``, ``contribution``)
or a module at its root (``api``, ``types``).  Each concept sits in one tier:
norms, computation or orchestration (``docs/engine/architecture.md``).  A
module imports at runtime only concepts of its own tier or of a lower one;
cycles inside a tier are allowed.

The roots of the layout by source (``contract``, ``tax``, ``payroll`` and the
root modules being renamed) are :data:`LEGACY_ROOTS`: the tier rule skips
them until their modules move into concepts, and the set only shrinks.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.integration.scripts.structure.support_imports import (
    ROOT_PACKAGE,
    runtime_imports,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from tests.integration.scripts.structure.support_imports import Import, Module

NORMS, COMPUTATION, ORCHESTRATION = 0, 1, 2
TIER_NAMES: tuple[str, ...] = ("norms", "computation", "orchestration")
#: Tier of every concept of the target tree.
CONCEPT_TIERS: Mapping[str, int] = {
    **dict.fromkeys(
        (
            "types",
            "validators",
            "errors",
            "version",
            "collection",
            "decision",
            "provenance",
            "run",
        ),
        NORMS,
    ),
    **dict.fromkeys(
        (
            "agreement",
            "knowledge",
            "limitation",
            "balance",
            "absence",
            "apprenticeship",
            "compensation",
            "contribution",
            "employer",
            "employment",
            "end_of_service",
            "event",
            "extra_month",
            "family",
            "fund",
            "irpef",
            "ledger",
            "pay_item",
            "pension_fund",
            "regime",
            "seniority",
            "severance",
            "sickness",
            "surtax",
            "tax_credit",
            "termination",
            "variable_pay",
            "withholding",
            "working_time",
        ),
        COMPUTATION,
    ),
    **dict.fromkeys(
        (
            "api",
            "inputs",
            "events",
            "results",
            "catalog",
            "assurance",
            "capability",
            "comparison",
            "default",
            "period",
            "reconciliation",
            "year",
        ),
        ORCHESTRATION,
    ),
}
#: Roots of the layout by source, outside the tier rule until they empty.
LEGACY_ROOTS: frozenset[str] = frozenset({
    "contract",
    "tax",
    "payroll",
    "primitives",
    "validation",
    "validation_collection",
})


def concept(name: str) -> str | None:
    """Return the concept of the ``ccnl_engine`` module *name*.

    Returns:
        The first name below the package, or None for the package root.
    """
    parts = name.split(".")
    return parts[1] if parts[0] == ROOT_PACKAGE and len(parts) > 1 else None


def _tiered(name: str) -> str | None:
    found = concept(name)
    return None if found is None or found in LEGACY_ROOTS else found


def unknown_concepts(modules: Mapping[str, Module]) -> list[str]:
    """Return the roots of the package that neither tier nor legacy lists.

    Returns:
        Sorted root names: a new concept needs a tier first.
    """
    roots = {concept(name) for name in modules} - {None}
    return sorted(
        str(root)
        for root in roots
        if root not in CONCEPT_TIERS and root not in LEGACY_ROOTS
    )


def stale_legacy_roots(modules: Mapping[str, Module]) -> list[str]:
    """Return the legacy roots no module lives under any more.

    Returns:
        Sorted names to remove from :data:`LEGACY_ROOTS`.
    """
    roots = {concept(name) for name in modules}
    return sorted(LEGACY_ROOTS - roots)


def _upward(imp: Import) -> tuple[str, str] | None:
    source, target = _tiered(imp.importer.name), _tiered(imp.target)
    if source is None or target is None or source == target:
        return None
    if CONCEPT_TIERS.get(source, NORMS) >= CONCEPT_TIERS.get(target, NORMS):
        return None
    return source, target


def tier_violations(
    modules: Mapping[str, Module], allowlist: Mapping[tuple[str, str], str]
) -> list[str]:
    """Return the runtime imports from a concept into a higher tier.

    An import is allowlisted by ``(importing concept, imported module or
    package)``.

    Returns:
        One ``path:line -> target (concept tier -> concept tier)`` line per
        import that no entry covers, in source order.
    """
    found: list[str] = []
    for imp in runtime_imports(modules):
        pair = _upward(imp)
        if pair is None or _allowed(pair[0], imp.target, allowlist):
            continue
        source, target = pair
        found.append(
            f"{imp.describe()} ({source} {TIER_NAMES[CONCEPT_TIERS[source]]} -> "
            f"{target} {TIER_NAMES[CONCEPT_TIERS[target]]})"
        )
    return found


def _allowed(
    source: str, target: str, allowlist: Mapping[tuple[str, str], str]
) -> bool:
    return any(
        owner == source and (target == prefix or target.startswith(f"{prefix}."))
        for owner, prefix in allowlist
    )


def stale_tier_entries(
    modules: Mapping[str, Module], allowlist: Mapping[tuple[str, str], str]
) -> list[tuple[str, str]]:
    """Return the allowlist entries no upward import uses.

    Returns:
        The unused entries, sorted: the allowlist only shrinks.
    """
    used = {
        (pair[0], prefix)
        for imp in runtime_imports(modules)
        if (pair := _upward(imp)) is not None
        for owner, prefix in allowlist
        if owner == pair[0]
        and (imp.target == prefix or imp.target.startswith(f"{prefix}."))
    }
    return sorted(set(allowlist) - used)
