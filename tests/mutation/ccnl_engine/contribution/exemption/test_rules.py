"""Caps, durations and codes of the contribution exemptions.

INPS circ. 90/2025: "€16,12 (€500/31 gg)" a day when the employment starts
or ends in the month, the cap cut in proportion for a part-time worker.
L. 199/2025 art. 1 c. 212: 12 months for a fixed term, 18 from the hire for
one made permanent, 24 for a permanent hire.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.contribution.exemption.inputs import (
    ContributionExemption,
    ExemptionMeasure,
)
from ccnl_engine.contribution.exemption.rules import (
    measure_rule,
    month_cap,
    months_of,
)
from ccnl_engine.errors import InvalidInputError

_START = date(2026, 1, 1)


@pytest.mark.parametrize(
    ("cap", "days", "part_time", "expected"),
    [
        ("500", None, None, "500.00"),
        ("500", 10, None, "161.20"),
        ("650", 31, None, "649.76"),
        ("666.66", 16, None, "344.00"),
        ("500", None, "0.5", "250.00"),
        ("500", 10, "0.625", "100.75"),
    ],
)
def test_the_cap_of_a_month(
    cap: str, days: int | None, part_time: str | None, expected: str
) -> None:
    """Whole month, 1/31 cut to the cent a day, times the part-time ratio."""
    ratio = None if part_time is None else Decimal(part_time)
    assert month_cap(Decimal(cap), days, ratio) == Decimal(expected)


@pytest.mark.parametrize(
    ("exemption", "fixed_term", "months"),
    [
        (ContributionExemption(ExemptionMeasure.YOUNG, _START), False, 24),
        (ContributionExemption(ExemptionMeasure.ZES, _START), True, 24),
        (ContributionExemption(ExemptionMeasure.MOTHERS, _START), False, 24),
        (ContributionExemption(ExemptionMeasure.MOTHERS, _START), True, 12),
        (
            ContributionExemption(
                ExemptionMeasure.MOTHERS, _START, made_permanent=True
            ),
            False,
            18,
        ),
    ],
)
def test_the_months_of_a_measure(
    exemption: ContributionExemption, fixed_term: bool, months: int
) -> None:
    """24 months; the mothers' hire 12 fixed term, 18 made permanent."""
    assert months_of(exemption, fixed_term=fixed_term) == months


@pytest.mark.parametrize(
    ("exemption", "cap", "code", "managers", "last"),
    [
        (
            ContributionExemption(ExemptionMeasure.YOUNG, _START),
            "500",
            "EG35",
            False,
            (2026, 4, 30),
        ),
        (
            ContributionExemption(ExemptionMeasure.YOUNG, _START, territorial=True),
            "650",
            "ES35",
            False,
            (2026, 4, 30),
        ),
        (
            ContributionExemption(ExemptionMeasure.WOMEN, _START),
            "650",
            "ED25",
            True,
            (2026, 12, 31),
        ),
        (
            ContributionExemption(ExemptionMeasure.WOMEN, _START, territorial=True),
            "650",
            "EDZE",
            True,
            (2026, 12, 31),
        ),
        (
            ContributionExemption(ExemptionMeasure.ZES, _START),
            "650",
            "EZES",
            False,
            (2026, 4, 30),
        ),
        (
            ContributionExemption(ExemptionMeasure.MOTHERS, _START),
            "666.66",
            "ELM3",
            True,
            (2026, 12, 31),
        ),
    ],
)
def test_the_rule_of_a_measure(
    exemption: ContributionExemption,
    cap: str,
    code: str,
    managers: bool,
    last: tuple[int, int, int],
) -> None:
    """Cap, UniEmens code, dirigenti and last hire of each measure."""
    rule = measure_rule(exemption)
    assert (rule.cap, rule.code, rule.managers) == (Decimal(cap), code, managers)
    assert rule.last_start == date(*last)


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"measure": "other"}, "measure"),
        ({"start": "2026-01-01"}, "start"),
        ({"share": Decimal("0.5")}, "0.7 or 1"),
        ({"measure": "women", "share": Decimal("0.7")}, "share"),
        ({"share": 1}, "share"),
        ({"measure": "zes", "territorial": True}, "territorial"),
        ({"made_permanent": True}, "made_permanent"),
        ({"territorial": "yes"}, "territorial"),
    ],
)
def test_invalid_exemption(kwargs: dict[str, object], message: str) -> None:
    """An unknown measure, a wrong type or a fact the measure does not read."""
    fields: dict[str, object] = {"measure": "young", "start": _START, **kwargs}
    with pytest.raises(InvalidInputError, match=message):
        ContributionExemption(**fields)  # type: ignore[arg-type]


def test_a_member_or_its_value() -> None:
    """The measure is stored as a member, from a member or its value."""
    by_value = ContributionExemption("zes", _START)  # type: ignore[arg-type]
    assert by_value.measure is ExemptionMeasure.ZES
