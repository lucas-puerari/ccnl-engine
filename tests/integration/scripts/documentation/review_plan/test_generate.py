"""The review plan groups the CCNLs by sector and orders them."""

from __future__ import annotations

import pytest

from scripts.documentation.review_plan.generate import (
    FIRST_ROUND,
    PAGE,
    Agreement,
    agreements,
    build_page,
    main,
    workers,
)


@pytest.mark.parametrize(
    ("text", "expected"),
    [("~120k", 120_000), ("35533", 35_533), ("~1.2M", 1_200_000), ("", 0), (None, 0)],
)
def test_workers_reads_the_estimate(text: object, expected: int) -> None:
    """Thousands, millions, plain numbers, nothing."""
    assert workers(text) == expected


def _agreement(slug: str, sector: str, workers_: int, weak: int) -> Agreement:
    return Agreement(
        slug, sector, workers_, "exploratory", None, None, False, weak, 0, 0
    )


def test_groups_follow_workers_then_weak_rules() -> None:
    """The larger group first; within it, the larger CCNL first."""
    page = build_page([
        _agreement("a", "small", 10, 9),
        _agreement("b", "big", 100, 0),
        _agreement("c", "big", 50, 5),
    ])

    assert page.index("## big") < page.index("## small")
    assert page.index("`b`") < page.index("`c`")


def test_the_bundled_plan_has_every_ccnl_and_every_anchor() -> None:
    """132 CCNLs in eight groups, the ten of the first round as anchors."""
    items = agreements()
    page = build_page(items)

    assert len(items) == 132
    assert len({a.sector for a in items}) == 8
    assert {a.slug for a in items} >= FIRST_ROUND
    assert page.count("(anchor)") == len(FIRST_ROUND)


def test_the_committed_page_is_up_to_date() -> None:
    """Regenerate with the script after any change of the bundle."""
    assert PAGE.read_text(encoding="utf-8") == build_page(agreements())
    assert main(["--check"]) == 0
