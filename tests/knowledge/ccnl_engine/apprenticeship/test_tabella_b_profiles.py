"""The Tabella B apprentices of DMO, Terziario Confesercenti and Commercio.

48 months for the profiles ending at levels II and III, 42 for those ending at
level IV; "2 livelli inferiori [...] per la prima metà del periodo di
apprendistato", "1 livello inferiore [...] per la seconda metà" (DMO Art. 46,
Terziario and Commercio Art. 53).
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.apprenticeship.rules import _apprentice_chain
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employment.inputs import Apprentice
from ccnl_engine.errors import OutOfScopeError

if TYPE_CHECKING:
    from decimal import Decimal

_DAY = date(2026, 6, 1)


def _base(slug: str, level: str, months: int, track: str | None) -> Decimal:
    ccnl = load_ccnl(slug)
    chain, _, _ = _apprentice_chain(
        ccnl,
        ccnl.level_by_code(level),
        Apprentice(months_elapsed=months, track=track),
        0,
        frozenset(),
        _DAY,
    )
    return chain.base


def _minimum(slug: str, level: str) -> Decimal | None:
    return load_ccnl(slug).level_by_code(level).base_salary.value_at(_DAY)


@pytest.mark.parametrize("slug", ["dmo-federdistribuzione", "terziario-confesercenti"])
@pytest.mark.parametrize(
    ("level", "track", "months", "paid_at"),
    [
        ("II", "tabella_b_48_mesi", 23, "IV"),
        ("II", "tabella_b_48_mesi", 24, "III"),
        ("III", "tabella_b_48_mesi", 47, "IV"),
        ("III", "tabella_b_48_mesi", 48, "III"),
        ("IV", "tabella_b_42_mesi", 20, "VI"),
        ("IV", "tabella_b_42_mesi", 21, "V"),
        ("IV", "tabella_b_42_mesi", 42, "IV"),
    ],
)
def test_the_long_profile_halves_its_own_duration(
    slug: str, level: str, track: str, months: int, paid_at: str
) -> None:
    """Two levels below for half the track, one below for the other half."""
    assert _base(slug, level, months, track) == _minimum(slug, paid_at)


@pytest.mark.parametrize("slug", ["dmo-federdistribuzione", "terziario-confesercenti"])
def test_a_level_with_a_long_track_needs_the_track(slug: str) -> None:
    """Levels II, III and IV have two tracks: the profile picks one."""
    with pytest.raises(OutOfScopeError, match="several apprenticeship tracks"):
        _base(slug, "IV", 0, None)


@pytest.mark.parametrize(
    ("level", "track", "months", "paid_at"),
    [
        ("2", "tabella_b_48_mesi", 23, "4"),
        ("3", "tabella_b_48_mesi", 24, "4"),
        ("4", "tabella_b_42_mesi", 20, "6"),
        ("4", "tabella_b_42_mesi", 42, "4"),
    ],
)
def test_commercio_halves_the_long_profiles_too(
    level: str, track: str, months: int, paid_at: str
) -> None:
    """Commercio Art. 68 (PDF pp. 82-83), its levels coded 2 to 7."""
    slug = "commercio-confcommercio"
    assert _base(slug, level, months, track) == _minimum(slug, paid_at)
