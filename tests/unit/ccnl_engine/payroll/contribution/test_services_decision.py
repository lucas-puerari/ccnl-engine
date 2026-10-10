"""Inputs the INPS decisions record about the minimum base."""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.payroll.contribution.models_minimum_base import (
    MinimumBase,
    MinimumBaseReason,
)
from ccnl_engine.payroll.contribution.services_decision import _minimum_inputs

_D = Decimal


def test_rules_without_a_minimum_say_so() -> None:
    """A repository whose INPS rules carry no minimum base."""
    assert _minimum_inputs(_D("1437.20"), None) == {"minimum_base": "not_modelled"}


def test_undetermined_minimum_records_none_and_its_bound() -> None:
    """An open minimum records the base, no minimum, the bound and why."""
    minimum = MinimumBase(_D("900"), _D("1511.38"), MinimumBaseReason.PARTIAL_MONTH)

    assert _minimum_inputs(_D("900"), minimum) == {
        "actual_base": _D("900"),
        "minimum_base": "none",
        "minimum_base_bound": _D("1511.38"),
        "minimum_base_reason": "partial_month",
    }
