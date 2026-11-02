"""The rules the NASpI contribution of an end of employment reports."""

from __future__ import annotations

from datetime import date
from types import SimpleNamespace
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.employment.period.inputs import (
    CollectiveDismissal,
    EmploymentPeriod,
    NaspiCase,
    TerminationCause,
)
from ccnl_engine.termination.naspi.loaders import load_naspi_dismissal_rules
from ccnl_engine.termination.naspi.services import naspi_rules

if TYPE_CHECKING:
    from ccnl_engine.provenance.source.rule.models import RuleProvenance

_NAME = "law/2026/naspi-dismissal"


def _rules(
    case: NaspiCase | CollectiveDismissal | None, year: int = 2026
) -> dict[str, RuleProvenance]:
    period = EmploymentPeriod(
        date(2016, 1, 1), date(year, 3, 10), TerminationCause.DISMISSAL, False, case
    )
    ctx = SimpleNamespace(request=SimpleNamespace(employment_period=period))
    return dict(naspi_rules(ctx))  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("case", "keys"),
    [
        (None, ("rate", "monthly_maximum")),
        (NaspiCase.ORDINARY, ("rate", "monthly_maximum")),
        (CollectiveDismissal(True, False), ("rate", "monthly_maximum")),
        (CollectiveDismissal(True, True), ("collective_rate", "monthly_maximum")),
        (
            CollectiveDismissal(False, False),
            ("rate", "monthly_maximum", "no_agreement_multiplier"),
        ),
        (
            CollectiveDismissal(False, True),
            ("collective_rate", "monthly_maximum", "no_agreement_multiplier"),
        ),
    ],
)
def test_the_rules_of_the_case_are_reported(
    case: NaspiCase | CollectiveDismissal | None, keys: tuple[str, ...]
) -> None:
    """The 82% and the multiplier only when the case uses them."""
    rules = load_naspi_dismissal_rules(2026)
    assert rules is not None

    found = _rules(case)

    assert list(found) == [f"{_NAME}:{key}" for key in keys]
    assert found == {f"{_NAME}:{key}": getattr(rules, key).provenance for key in keys}


def test_a_year_without_rules_reports_none() -> None:
    """2027 has no NASpI maximum yet."""
    assert _rules(None, 2027) == {}
