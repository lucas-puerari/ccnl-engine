"""Ruleset version and verification identity helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.knowledge.version import __version__ as knowledge_version

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import CCNL
    from ccnl_engine.engine.payroll.service.fiscal import FiscalPay
    from ccnl_engine.engine.payroll.service.work_rules import WorkRulesPay
    from ccnl_engine.engine.surtax.domain.rules import SurtaxRules
    from ccnl_engine.engine.tax.domain.rules import YearRules


def _surtax_versions(surtax: SurtaxRules) -> dict[str, str]:
    """Return ``{surtax_regional: ..., surtax_municipal: ...}`` identity strings.

    Both keys are always emitted when the surtax bundle is loaded: the envelope
    documents which data files were read and validated, regardless of whether a
    specific jurisdiction entry was looked up.

    Returns:
        Mapping with ``surtax_regional`` and ``surtax_municipal`` keys.
    """
    suffix = f"surtax/{surtax.year}"
    return {
        "surtax_regional": (
            str(surtax.regional_ruleset)
            if surtax.regional_ruleset is not None
            else f"{suffix}/regional@{knowledge_version}"
        ),
        "surtax_municipal": (
            str(surtax.municipal_ruleset)
            if surtax.municipal_ruleset is not None
            else f"{suffix}/municipal@{knowledge_version}"
        ),
    }


def _ruleset_versions(
    ccnl: CCNL,
    rules: YearRules,
    surtax: SurtaxRules | None,
    sub_rulesets: dict[str, str] | None = None,
    *,
    uses_family_deductions: bool = False,
    uses_art15_deductions: bool = False,
) -> dict[str, str]:
    """Return ``{kind: id@version}`` identities for all consumed rulesets.

    Falls back to the knowledge-base version for rulesets without a recorded
    identity.  Sub-rulesets (e.g. ``sick_pay``, ``variable_pay``) are merged
    in only when provided.

    When ``uses_family_deductions`` is ``True``, a ``"family_deductions"`` key
    is added for the ``family-deductions-{year}.json`` data file, which is a
    separate ruleset from the main tax file.  Likewise for
    ``uses_art15_deductions`` and ``"art15_deductions"``.

    Returns:
        Mapping of ruleset kind to ``id@version`` string.
    """
    versions: dict[str, str] = {}
    if ccnl.ruleset is not None:
        versions["ccnl"] = str(ccnl.ruleset)
    else:
        versions["ccnl"] = f"{ccnl.meta.ccnl_id}@{knowledge_version}"
    if rules.ruleset is not None:
        versions["tax"] = str(rules.ruleset)
    else:
        versions["tax"] = f"tax/{rules.year}/{ccnl.meta.tax_sector}@{knowledge_version}"
    if rules.inps_ruleset is not None:
        versions["inps"] = str(rules.inps_ruleset)
    elif rules.domestic_contributions is None:
        # Standard percentage model: INPS rules were consumed but the identity
        # block is absent — emit a fallback so every consumed ruleset appears.
        versions["inps"] = (
            f"inps/{rules.year}/{ccnl.meta.tax_sector}@{knowledge_version}"
        )
    if surtax is not None:
        versions.update(_surtax_versions(surtax))
    if uses_family_deductions:
        versions["family_deductions"] = (
            f"family-deductions/{rules.year}@{knowledge_version}"
        )
    if uses_art15_deductions:
        versions["art15_deductions"] = (
            f"art15-deductions/{rules.year}@{knowledge_version}"
        )
    if sub_rulesets:
        versions.update(sub_rulesets)
    return versions


def _ruleset_verifications(
    ccnl: CCNL,
    rules: YearRules,
    surtax: SurtaxRules | None,
    work: WorkRulesPay,
    fiscal: FiscalPay,
) -> dict[str, str]:
    """Return ``{kind: verification_status}`` for all consumed rulesets.

    Mirrors :func:`_ruleset_versions` but records the
    :class:`~ccnl_engine.engine.metadata.domain.rules.VerificationStatus`
    value of each ruleset instead of its ``id@version`` string.  Missing
    or absent identities default to ``"unverified"``.

    Returns:
        Mapping of ruleset kind to verification status string.
    """
    unverified = "unverified"
    ver: dict[str, str] = {}
    ver["ccnl"] = (
        ccnl.ruleset.verification_status.value
        if ccnl.ruleset is not None
        else unverified
    )
    ver["tax"] = (
        rules.ruleset.verification_status.value
        if rules.ruleset is not None
        else unverified
    )
    if rules.inps_ruleset is not None:
        ver["inps"] = rules.inps_ruleset.verification_status.value
    elif rules.domestic_contributions is None:
        ver["inps"] = unverified
    if surtax is not None:
        ver["surtax_regional"] = (
            surtax.regional_ruleset.verification_status.value
            if surtax.regional_ruleset is not None
            else unverified
        )
        ver["surtax_municipal"] = (
            surtax.municipal_ruleset.verification_status.value
            if surtax.municipal_ruleset is not None
            else unverified
        )
    ver.update(fiscal.consumed_verifications)
    ver.update(work.consumed_verifications)
    return ver
