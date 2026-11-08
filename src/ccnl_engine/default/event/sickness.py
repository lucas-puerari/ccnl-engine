"""Defaults of the public sickness-episode event facts."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.default.models import (
    FactEnforcement,
    absence_is_fact,
    requires_fact,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.default.models import FieldDefault

SICKNESS_DEFAULTS: Mapping[str, FieldDefault] = {
    "SicknessEpisode.periodic_check": absence_is_fact("an ordinary sickness absence"),
    "SicknessEpisode.daily_contributions": requires_fact(
        "sickness",
        "event.daily_contributions",
        FactEnforcement.REPORTED,
        "unknown contributions: an INPS regime with a requirement pays its "
        "share, with a provisional sickness_daily_contributions_unknown issue",
    ),
    "SicknessEpisode.serious_illness": requires_fact(
        "sickness",
        "event.serious_illness",
        FactEnforcement.REPORTED,
        "unknown seriousness: a CCNL with a serious-illness treatment pays "
        "the episode as an ordinary one, with a provisional "
        "sickness_serious_illness_unknown issue",
    ),
    "SicknessEpisode.serious_illness_kind": absence_is_fact(
        "the ordinary comporto and sick-pay limit; extended eligibility requires "
        "a documented qualifying condition (including a current specialist "
        "certificate for a listed grave pathology, certified L. 68/99 civil "
        "disability, or certified life-saving therapy related to either condition)"
    ),
    "SicknessEpisode.excluded_comporto_days": absence_is_fact("every sick day counts"),
    "SicknessEpisode.prior_worked_days": requires_fact(
        "sickness",
        "event.prior_worked_days",
        FactEnforcement.REPORTED,
        "unknown days of work before a fixed-term episode: the D.L. 463/1983 "
        "art. 5 limit is not applied, with a provisional "
        "sickness_fixed_term_prior_work_unknown issue",
    ),
    "SicknessEpisode.agricultural_days": requires_fact(
        "sickness",
        "event.agricultural_days",
        FactEnforcement.REPORTED,
        "unknown days in the elenchi of an operaio agricolo a tempo "
        "determinato: INPS pays up to 180 days a year, with a provisional "
        "sickness_agricultural_days_unknown issue",
    ),
    "SicknessEpisode.short_absence_exempt": requires_fact(
        "sickness",
        "event.short_absence_exempt",
        FactEnforcement.REPORTED,
        "unknown exemption: a short absence the CCNL could pay less has a "
        "missing_fact short_absence_exempt blocker and is paid unreduced",
    ),
}
