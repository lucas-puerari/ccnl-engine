"""A shrink-only baseline may shrink, never grow, against its base."""

from __future__ import annotations

from scripts.quality.baseline.check import (
    READINESS,
    SIZE,
    main,
    readiness_growth,
    size_growth,
)


def test_a_new_readiness_gap_is_growth() -> None:
    """A gap the base does not list is reported, a closed one is not."""
    base: dict[str, dict[str, list[str]]] = {
        "any": {},
        "provider output": {"a": ["gross", "net"]},
    }
    head = {"any": {"b": ["tax"]}, "provider output": {"a": ["gross"]}}

    assert readiness_growth(base, head) == [f"{READINESS}: new gap any / b / tax"]


def test_a_new_or_longer_module_is_growth() -> None:
    """A module may shrink or leave the baseline, not enter it or grow."""
    base = {"x.py": 320, "y.py": 310, "z.py": 305}
    head = {"x.py": 330, "y.py": 300, "w.py": 301}

    assert size_growth(base, head) == [
        f"{SIZE}: w.py new -> 301 lines",
        f"{SIZE}: x.py 320 -> 330 lines",
    ]


def test_the_tree_does_not_grow_against_itself() -> None:
    """Against HEAD the working baselines are unchanged."""
    assert main(["--base", "HEAD"]) == 0
