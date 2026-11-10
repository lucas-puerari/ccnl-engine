"""Mutations in the wood-sector clerical apprenticeship percentage tracks."""

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.apprenticeship.rules import _apprentice_chain
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employment.inputs import Apprentice
from ccnl_engine.errors import OutOfScopeError
from ccnl_engine.pay_item.rounding.policies import money

_SLUG = "legno-lapidei-artigianato-confartigianato"
_AS_OF = date(2026, 11, 1)


def test_impiegato_group_3_sixth_semester_vs_operaio_completion() -> None:
    """Compare the third-year impiegato against the operai track.

    Month 31: E base EUR 1,585.97 x 95% = EUR 1,506.67 for the impiegato;
    the operai track has ended its fifth semester and returns 100%,
    EUR 1,585.97. The difference is EUR 79.30.
    """
    ccnl = load_ccnl(_SLUG)
    level = ccnl.level_by_code("E")
    clerical, clerical_pct, _ = _apprentice_chain(
        ccnl,
        level,
        Apprentice(30, track="gruppo_3_legno_impiegati"),
        1,
        frozenset(),
        _AS_OF,
    )
    manual, manual_pct, _ = _apprentice_chain(
        ccnl, level, Apprentice(30, track="gruppo_3_legno"), 1, frozenset(), _AS_OF
    )
    assert clerical_pct == Decimal("0.95")
    assert manual_pct == Decimal("1.00")
    assert money(clerical.base * clerical_pct) == Decimal("1506.67")
    assert money(manual.base * manual_pct) == Decimal("1585.97")


@pytest.mark.parametrize(
    ("level_code", "track_name", "expected"),
    [
        ("B", "gruppo_1_legno_impiegati", Decimal("0.80")),
        ("D", "gruppo_2_legno_impiegati", Decimal("0.88")),
        ("E", "gruppo_3_legno_impiegati", Decimal("0.95")),
    ],
)
def test_clerical_third_year_requires_explicit_track(
    level_code: str, track_name: str, expected: Decimal
) -> None:
    """Overlapping operai and impiegati levels require a selected track."""
    ccnl = load_ccnl(_SLUG)
    level = ccnl.level_by_code(level_code)
    with pytest.raises(OutOfScopeError, match="several apprenticeship tracks"):
        _apprentice_chain(ccnl, level, Apprentice(30), 1, frozenset(), _AS_OF)
    _, percentage, _ = _apprentice_chain(
        ccnl, level, Apprentice(30, track=track_name), 1, frozenset(), _AS_OF
    )
    assert percentage == expected
