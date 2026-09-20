"""Collect consumed ruleset identities and verification statuses for fiscal stages."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.service.fiscal_helpers import _vs

if TYPE_CHECKING:
    from ccnl_engine.engine.metadata import RulesetIdentity
    from ccnl_engine.engine.payroll.domain._internal_scenario import _InternalScenario
    from ccnl_engine.engine.surtax.domain.rules import SurtaxRules


def _collect_fiscal_rulesets(
    fam_ruleset: RulesetIdentity | None,
    art15_ruleset: RulesetIdentity | None,
    surtax_regional_ruleset: RulesetIdentity | None,
    surtax_municipal_ruleset: RulesetIdentity | None,
    *,
    family_consumed: bool,
    art15_consumed: bool,
    surtax_reg_consumed: bool,
    surtax_com_consumed: bool,
) -> tuple[RulesetIdentity | None, ...]:
    """Return the ordered tuple of optional-feature ruleset identities.

    Returns:
        A tuple with at most four entries: family deductions, Art. 15,
        surtax regional and surtax municipal.
    """
    ids: list[RulesetIdentity | None] = []
    if fam_ruleset is not None or family_consumed:
        ids.append(fam_ruleset)
    if art15_ruleset is not None or art15_consumed:
        ids.append(art15_ruleset)
    if surtax_reg_consumed:
        ids.append(surtax_regional_ruleset)
    if surtax_com_consumed:
        ids.append(surtax_municipal_ruleset)
    return tuple(ids)


def _collect_fiscal_verifications(
    fam_ruleset: RulesetIdentity | None,
    art15_ruleset: RulesetIdentity | None,
    surtax_reg_id: RulesetIdentity | None,
    surtax_com_id: RulesetIdentity | None,
    *,
    family_consumed: bool,
    art15_consumed: bool,
    surtax_reg_consumed: bool,
    surtax_com_consumed: bool,
) -> dict[str, str]:
    """Return ``{kind: verification_status}`` for optional fiscal rulesets.

    Returns:
        Mapping of ruleset kind to verification status string.
    """
    ver: dict[str, str] = {}
    if family_consumed:
        ver["family_deductions"] = _vs(fam_ruleset)
    if art15_consumed:
        ver["art15_deductions"] = _vs(art15_ruleset)
    if surtax_reg_consumed:
        ver["surtax_regional"] = _vs(surtax_reg_id)
    if surtax_com_consumed:
        ver["surtax_municipal"] = _vs(surtax_com_id)
    return ver


def _fiscal_consumed(
    scenario: _InternalScenario,
    surtax: SurtaxRules | None,
    fam_ruleset: RulesetIdentity | None,
    art15_ruleset: RulesetIdentity | None,
    *,
    has_any_dependent: bool,
    surtax_reg_consumed: bool,
    surtax_com_consumed: bool,
) -> tuple[tuple[RulesetIdentity | None, ...], dict[str, str]]:
    """Return ``(consumed_ids, consumed_verifications)`` for optional fiscal rulesets.

    Returns:
        2-tuple of consumed ruleset identity tuple and verification mapping.
    """
    art15_used = (
        scenario.art15_deductions is not None
        and scenario.art15_deductions.has_any_onere
    )
    surtax_reg_id = surtax.regional_ruleset if surtax is not None else None
    surtax_com_id = surtax.municipal_ruleset if surtax is not None else None
    ids = _collect_fiscal_rulesets(
        fam_ruleset,
        art15_ruleset,
        surtax_reg_id,
        surtax_com_id,
        family_consumed=has_any_dependent,
        art15_consumed=art15_used,
        surtax_reg_consumed=surtax_reg_consumed,
        surtax_com_consumed=surtax_com_consumed,
    )
    ver = _collect_fiscal_verifications(
        fam_ruleset,
        art15_ruleset,
        surtax_reg_id,
        surtax_com_id,
        family_consumed=has_any_dependent,
        art15_consumed=art15_used,
        surtax_reg_consumed=surtax_reg_consumed,
        surtax_com_consumed=surtax_com_consumed,
    )
    return ids, ver
