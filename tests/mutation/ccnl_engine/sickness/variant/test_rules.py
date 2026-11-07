"""Sick-leave rules of a worker category or of apprentices.

Tabacco art. 34 pays the impiegati and quadri by seniority over 12 months
of comporto, the operai 100% for 180 days; Federalimentare art. 21 pays
the apprentice the normal pay for at most six months a year.
"""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employment.apprentice.inputs import Apprentice
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.sickness.variant.rules import with_sickness_variant

_TABACCO = load_ccnl("tabacco-apti")
_ALIMENTARI = load_ccnl("alimentari-federalimentare")


def _rules(ccnl: object) -> object:
    return ccnl.work_rules.sickness_rules  # type: ignore[attr-defined]


def test_tabacco_operai_keep_the_general_rule() -> None:
    """Operai: 100% for 180 days, no cumulation."""
    rules = _rules(with_sickness_variant(_TABACCO, WorkerCategory.OPERAIO, None))
    assert rules.max_duration_days == 180  # type: ignore[attr-defined]
    assert rules.cumulation is None  # type: ignore[attr-defined]


def test_tabacco_impiegati_and_quadri_take_the_twelve_months() -> None:
    """4+4, 5+5, 6+6 months over 365 days of comporto, counted over the chain."""
    for category in (WorkerCategory.IMPIEGATO, WorkerCategory.QUADRO):
        cumulation = _rules(with_sickness_variant(_TABACCO, category, None)).cumulation  # type: ignore[attr-defined]
        assert cumulation.comporto_over_chain
        assert cumulation.reset_after_days == 365
        assert [
            (b.seniority_months_from, b.full_pay_days, b.comporto_days)
            for b in cumulation.bands
        ] == [
            (0, 120, 365),
            (60, 150, 365),
            (121, 180, 365),
        ]
        assert [b.step_rate(2 * b.full_pay_days) for b in cumulation.bands] == [
            Decimal("0.5")
        ] * 3
        assert [b.step_rate(2 * b.full_pay_days + 1) for b in cumulation.bands] == [
            None
        ] * 3


def test_without_a_category_the_general_rule_holds() -> None:
    """No category, no variant."""
    assert with_sickness_variant(_TABACCO, None, None) is _TABACCO


def test_an_alimentari_apprentice_takes_six_months_a_year() -> None:
    """Art. 21: 100% of the gross pay, 180 days in the calendar year."""
    rules = _rules(
        with_sickness_variant(
            _ALIMENTARI, WorkerCategory.OPERAIO, Apprentice(months_elapsed=6)
        )
    )
    assert rules.carenza_integration_rate == rules.full_pay_integration_rate == 1  # type: ignore[attr-defined]
    assert not rules.net_basis  # type: ignore[attr-defined]
    assert rules.comporto_calendar_year  # type: ignore[attr-defined]
    assert rules.max_duration_days == 180  # type: ignore[attr-defined]


def test_an_alimentari_employee_keeps_the_general_rule() -> None:
    """Not an apprentice and no category rule: the CCNL is unchanged."""
    assert (
        with_sickness_variant(_ALIMENTARI, WorkerCategory.OPERAIO, None) is _ALIMENTARI
    )


def test_a_ccnl_without_work_rules_is_unchanged() -> None:
    """Nothing to vary."""
    bare = _TABACCO.model_copy(update={"work_rules": None})
    assert (
        with_sickness_variant(
            bare, WorkerCategory.IMPIEGATO, Apprentice(months_elapsed=1)
        )
        is bare
    )
