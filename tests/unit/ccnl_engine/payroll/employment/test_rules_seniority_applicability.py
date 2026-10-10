"""Whether a level pays seniority increments, from the shape of the rules."""

from __future__ import annotations

from typing import Any

import pytest

from ccnl_engine.contract.employment.models_category import WorkerCategory
from ccnl_engine.contract.seniority.models import SeniorityIncrements
from ccnl_engine.payroll.employment.rules_seniority import increments_apply
from tests.helpers import TEST_PROV, _series

_OPERAIO = WorkerCategory.OPERAIO
_IMPIEGATO = WorkerCategory.IMPIEGATO


def _rules(**fields: Any) -> SeniorityIncrements:  # noqa: ANN401
    """Build seniority rules: flat, 24-month cadence, five increments on L1.

    Returns:
        The rules with ``fields`` replacing the defaults.
    """
    raw: dict[str, Any] = {
        "cadence_months": 24,
        "maximum_count": 5,
        "amount_by_level": {"L1": _series("10.00")},
        "provenance": TEST_PROV,
    }
    raw.update(fields)
    return SeniorityIncrements.model_validate(raw)


def _by_category() -> SeniorityIncrements:
    return _rules(
        amount_by_level={},
        amount_by_level_by_category={"operaio": {"L1": _series("10.00")}},
    )


class TestIncrementsApply:
    """The fact is needed only where the rules can pay an increment."""

    def test_level_with_an_amount(self) -> None:
        """A level of the flat table is paid increments."""
        assert increments_apply(_rules(), "L1", None, apprentice=False)

    def test_level_without_an_amount(self) -> None:
        """A level missing from the table is not."""
        assert not increments_apply(_rules(), "L2", None, apprentice=False)

    def test_zero_maximum(self) -> None:
        """A CCNL without increments (maximum zero) pays none."""
        rules = _rules(maximum_count=0, amount_by_level={})
        assert not increments_apply(rules, "L1", None, apprentice=False)

    def test_excluded_category(self) -> None:
        """An excluded category is paid none, e.g. operai edili via APE."""
        rules = _rules(excluded_categories=["operaio"])
        assert not increments_apply(rules, "L1", _OPERAIO, apprentice=False)
        assert increments_apply(rules, "L1", _IMPIEGATO, apprentice=False)

    def test_zero_maximum_of_the_category(self) -> None:
        """A category whose maximum is zero is paid none."""
        rules = _rules(maximum_count_by_category={"operaio": 0})
        assert not increments_apply(rules, "L1", _OPERAIO, apprentice=False)

    @pytest.mark.parametrize(
        ("category", "expected"),
        [(_OPERAIO, True), (_IMPIEGATO, False), (None, True)],
        ids=["paid-category", "other-category", "unknown-category"],
    )
    def test_amount_by_category(
        self, category: WorkerCategory | None, expected: bool
    ) -> None:
        """A per-category table pays its category; unknown counts as paid."""
        assert (
            increments_apply(_by_category(), "L1", category, apprentice=False)
            is expected
        )

    def test_unknown_category_on_a_level_no_category_lists(self) -> None:
        """No category table lists the level: nothing to pay."""
        assert not increments_apply(_by_category(), "L2", None, apprentice=False)

    def test_apprentice_amount(self) -> None:
        """An apprentice amount pays apprentices on any level."""
        rules = _rules(apprentice_amount=_series("5.00"))
        assert increments_apply(rules, "L9", None, apprentice=True)
        assert not increments_apply(rules, "L9", None, apprentice=False)

    def test_tiers(self) -> None:
        """A tiered ladder pays the levels its tiers list."""
        tier = {
            "cadence_months": 24,
            "maximum_count": 2,
            "amount_by_level": {"L1": _series("10.00")},
        }
        rules = _rules(maximum_count=2, amount_by_level={}, tiers=[tier])
        assert increments_apply(rules, "L1", None, apprentice=False)
        assert not increments_apply(rules, "L2", None, apprentice=False)
