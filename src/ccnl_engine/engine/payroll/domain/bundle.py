"""Immutable payroll knowledge bundle."""

from __future__ import annotations

import dataclasses
import hashlib
import json
from typing import TYPE_CHECKING

from ccnl_engine.knowledge.version import __version__ as _knowledge_version

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import CCNL
    from ccnl_engine.engine.surtax.domain.rules import SurtaxRules
    from ccnl_engine.engine.tax.domain.rules import YearRules


@dataclasses.dataclass(frozen=True)
class PayrollBundle:
    """Pre-loaded, frozen knowledge bundle for reproducible payroll computation.

    Groups the three ruleset objects consumed by the payroll engine into a
    single value together with a deterministic content hash.  Passing a bundle
    to :func:`~ccnl_engine.compute` or :func:`~ccnl_engine.estimate_annual`
    skips rule loading and guarantees every computation in the same payroll run
    uses identical data.

    Obtain one via :func:`~ccnl_engine.engine.payroll.service.bundle_loader\
.load_payroll_bundle`.  The hash is reproduced in
    :attr:`~ccnl_engine.engine.payroll.domain.calculation.Calculation\
.ruleset_version` so audit trails are self-contained.

    Attributes:
        ccnl: Loaded, frozen CCNL contract rules.
        rules: Loaded, frozen annual tax/INPS rules.
        surtax: Loaded, frozen surtax rates; ``None`` when no jurisdiction
            is needed.
        bundle_hash: SHA-256 hex-digest of the canonical version-string map,
            computed at construction time.
    """

    ccnl: CCNL
    rules: YearRules
    surtax: SurtaxRules | None
    bundle_hash: str


def _compute_bundle_hash(
    ccnl: CCNL,
    rules: YearRules,
    surtax: SurtaxRules | None,
) -> str:
    """Return a SHA-256 hex-digest of the bundle's canonical version-string map.

    The digest is computed from the sorted JSON of a ``{kind: id@version}``
    mapping identical in structure to
    :attr:`~ccnl_engine.engine.payroll.domain.calculation.Calculation\
.ruleset_version`.  Absent identity blocks fall back to the knowledge-version
    tag so the hash always covers every consumed ruleset.

    Returns:
        64-character lowercase hex-string.
    """
    kv = _knowledge_version
    versions: dict[str, str] = {}
    if ccnl.ruleset is not None:
        versions["ccnl"] = str(ccnl.ruleset)
    else:
        versions["ccnl"] = f"{ccnl.meta.ccnl_id}@{kv}"
    if rules.ruleset is not None:
        versions["tax"] = str(rules.ruleset)
    else:
        versions["tax"] = f"tax/{rules.year}/{ccnl.meta.tax_sector}@{kv}"
    if rules.inps_ruleset is not None:
        versions["inps"] = str(rules.inps_ruleset)
    elif rules.domestic_contributions is None:
        versions["inps"] = f"inps/{rules.year}/{ccnl.meta.tax_sector}@{kv}"
    if surtax is not None:
        versions["surtax_regional"] = (
            str(surtax.regional_ruleset)
            if surtax.regional_ruleset is not None
            else f"surtax/{surtax.year}/regional@{kv}"
        )
        versions["surtax_municipal"] = (
            str(surtax.municipal_ruleset)
            if surtax.municipal_ruleset is not None
            else f"surtax/{surtax.year}/municipal@{kv}"
        )
    canonical = json.dumps(versions, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()


def make_bundle(
    ccnl: CCNL,
    rules: YearRules,
    surtax: SurtaxRules | None,
) -> PayrollBundle:
    """Construct a :class:`PayrollBundle` with a freshly computed hash.

    This is the canonical factory.  Pass the objects returned by the individual
    loaders; the hash is computed automatically.

    Returns:
        An immutable :class:`PayrollBundle` ready for passing to
        :func:`~ccnl_engine.engine.payroll.service.orchestrator.compute`.
    """
    return PayrollBundle(
        ccnl=ccnl,
        rules=rules,
        surtax=surtax,
        bundle_hash=_compute_bundle_hash(ccnl, rules, surtax),
    )
