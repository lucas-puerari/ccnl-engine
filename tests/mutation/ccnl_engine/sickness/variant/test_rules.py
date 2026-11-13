"""Sick-leave rules of a worker category or of apprentices.

Tabacco art. 34 pays the impiegati and quadri by seniority over 12 months
of comporto, the operai 100% for 180 days; Federalimentare art. 21 pays
the apprentice the normal pay for at most six months a year.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employment.apprentice.inputs import Apprentice
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.employment.inputs import FixedTerm, Permanent
from ccnl_engine.sickness.variant.rules import with_sickness_variant

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.sickness.integration.models import SicknessRules

_TABACCO = load_ccnl("tabacco-apti")
_ALIMENTARI = load_ccnl("alimentari-federalimentare")


def _rules(ccnl: CCNL) -> SicknessRules:
    assert ccnl.work_rules is not None
    rules = ccnl.work_rules.sickness_rules
    assert rules is not None
    return rules


def test_tabacco_operai_keep_the_general_rule() -> None:
    """Operai: 100% for 180 days, no cumulation."""
    rules = _rules(with_sickness_variant(_TABACCO, WorkerCategory.OPERAIO, None))
    assert rules.max_duration_days == 180
    assert rules.cumulation is None


def test_tabacco_impiegati_and_quadri_take_the_twelve_months() -> None:
    """4+4, 5+5, 6+6 months over 365 days of comporto, counted over the chain."""
    for category in (WorkerCategory.IMPIEGATO, WorkerCategory.QUADRO):
        cumulation = _rules(
            with_sickness_variant(_TABACCO, category, Permanent())
        ).cumulation
        assert cumulation is not None
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
    assert rules.carenza_integration_rate == rules.full_pay_integration_rate == 1
    assert not rules.net_basis
    assert rules.comporto_calendar_year
    assert rules.max_duration_days == 180


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


def test_a_fixed_term_impiegato_keeps_the_general_rule() -> None:
    """Art. 34: the 12 months are of the impiegato 'a tempo indeterminato'."""
    fixed = FixedTerm()
    rules = _rules(with_sickness_variant(_TABACCO, WorkerCategory.IMPIEGATO, fixed))
    assert rules.cumulation is None
    assert rules.max_duration_days == 180


def test_a_permanent_impiegato_takes_the_twelve_months() -> None:
    """The same worker on a permanent contract."""
    rules = _rules(
        with_sickness_variant(_TABACCO, WorkerCategory.IMPIEGATO, Permanent())
    )
    assert rules.cumulation is not None


def test_a_tabacco_apprentice_takes_half_pay_six_months_a_year() -> None:
    """Art. 6: 50% of the normal pay for at most 6 months a year."""
    apprentice = Apprentice(months_elapsed=3)
    rules = _rules(
        with_sickness_variant(_TABACCO, WorkerCategory.IMPIEGATO, apprentice)
    )
    assert (
        rules.carenza_integration_rate
        == rules.full_pay_integration_rate
        == Decimal("0.5")
    )
    assert rules.comporto_calendar_year
    assert rules.max_duration_days == 180


@pytest.mark.parametrize(
    "slug",
    ["commercio-confcommercio", "terziario-confesercenti", "dmo-federdistribuzione"],
)
def test_a_terziario_apprentice_takes_the_sixty_percent(slug: str) -> None:
    """Art. 54 (DMO art. 47): 60% gross carenza for six events, 60% in hospital."""
    rules = _rules(
        with_sickness_variant(
            load_ccnl(slug), WorkerCategory.IMPIEGATO, Apprentice(months_elapsed=6)
        )
    )
    events = rules.carenza_by_event
    assert events is not None
    assert (events.from_event, events.rates, events.exemptions) == (
        7,
        (Decimal(0),),
        False,
    )
    assert rules.carenza_integration_rate == rules.hospital_employer_share
    assert rules.carenza_integration_rate == Decimal("0.6")
    assert rules.full_pay_integration_rate == 0
    assert rules.after_probation
    assert not rules.net_basis
    assert not rules.apprentices_excluded
    assert rules.comporto_calendar_year
    assert rules.max_duration_days == 180
