"""The months of service and the cases of the NASpI contribution.

INPS circ. 44/2013 par. 2: a month of at least 15 calendar days counts
whole; the 2026 maximum of 1584.70 (INPS circ. 4/2026 par. 6) gives
649.73 for twelve months, 1949.19 for 36, and 541.44 for ten (649.73 /
12 * 10 = 541.4417, note 6 of the circular).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.employment.period.inputs import TerminationCause
from ccnl_engine.inputs import Apprentice, FixedTerm, Permanent
from ccnl_engine.termination.naspi.loaders import load_naspi_dismissal_rules
from ccnl_engine.termination.naspi.rules import (
    dismissal_contribution,
    is_due,
    service_months,
)

_D, _R = TerminationCause.DISMISSAL, TerminationCause.RESIGNATION


@pytest.mark.parametrize(
    ("started", "ended", "months"),
    [
        (date(2016, 1, 1), date(2026, 3, 10), 36),
        (date(2023, 3, 11), date(2026, 3, 10), 36),
        (date(2025, 1, 1), date(2025, 10, 31), 10),
        (date(2025, 1, 17), date(2025, 10, 31), 10),
        (date(2025, 1, 18), date(2025, 10, 31), 9),
        (date(2025, 1, 18), date(2025, 10, 14), 8),
        (date(2025, 1, 1), date(2025, 10, 15), 10),
        (date(2026, 2, 1), date(2026, 2, 14), 0),
        (date(2024, 2, 29), date(2024, 3, 31), 1),
        (date(2016, 1, 1), date(2024, 2, 29), 36),
        (date(2016, 1, 1), date(2026, 2, 14), 35),
        (date(2026, 2, 1), date(2026, 2, 15), 1),
    ],
)
def test_months_of_at_least_15_days_count_whole(
    started: date, ended: date, months: int
) -> None:
    """The service of the last three years, by months of 15 days or more.

    Ending on 14 February 2026, the three years start on 15 February 2023:
    14 days of February at each end, 35 months.
    """
    assert service_months(started, ended) == months


@pytest.mark.parametrize(
    ("cause", "just_cause", "contract", "due"),
    [
        (_D, False, Permanent(), True),
        (_D, True, Apprentice(months_elapsed=6), True),
        (_R, True, Permanent(), True),
        (_R, True, Apprentice(months_elapsed=6), True),
        (_R, False, Permanent(), False),
        (_R, None, Permanent(), None),
        (TerminationCause.MUTUAL_AGREEMENT, None, Permanent(), False),
        (TerminationCause.DEATH, None, Permanent(), False),
        (_D, False, FixedTerm(), False),
    ],
)
def test_the_causes_that_owe_it(
    cause: TerminationCause,
    just_cause: bool | None,
    contract: Permanent | Apprentice | FixedTerm,
    due: bool | None,
) -> None:
    """Art. 2 cc. 31-32 L. 92/2012 and INPS circ. 44/2013 par. 1."""
    assert is_due(cause, just_cause, contract) is due


@pytest.mark.parametrize(
    ("months", "amount"), [(36, "1949.19"), (12, "649.73"), (10, "541.44")]
)
def test_the_contribution_of_2026(months: int, amount: str) -> None:
    """41% of 1584.70 for each twelve months, pro rata."""
    rules = load_naspi_dismissal_rules(2026)

    assert rules is not None
    assert dismissal_contribution(rules, months) == Decimal(amount)
    assert load_naspi_dismissal_rules(2027) is None


@pytest.mark.parametrize(("months", "amount"), [(10, "403.16"), (36, "1451.40")])
def test_the_examples_of_circ_44_2013(months: int, amount: str) -> None:
    """The 2013 maximum of 1180.00: 483.80 a year, a twelfth a month."""
    rules = load_naspi_dismissal_rules(2026)
    assert rules is not None
    maximum = rules.monthly_maximum.model_copy(update={"value": Decimal(1180)})
    rules = rules.model_copy(update={"monthly_maximum": maximum})

    assert dismissal_contribution(rules, months) == Decimal(amount)
