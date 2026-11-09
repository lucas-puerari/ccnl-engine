"""Hand oracle: ANCE Art. 92, cached PDF p. 6, first-level extension.

At the June 2026 conventional level 1, base 1,117.36: month 36 normally
pays 90% = 1,005.624 -> 1,005.62; the failed-title extension retains
month 24's 85% = 949.756 -> 949.76. Month 42 instead retains month 30's
90% = 1,005.62. No extension input keeps the ordinary progression.
"""

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.apprenticeship.dual.rules import dual_chain
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employment.apprentice.inputs import (
    Apprentice,
    ApprenticeshipProgramme,
    DualHours,
)
from ccnl_engine.errors import (
    InvalidInputError,
    MissingRequiredFactError,
    OutOfScopeError,
)


@pytest.mark.parametrize("agreement", ["edilizia-ance", "edilizia-ance-impiegati"])
@pytest.mark.parametrize(
    ("month", "start", "expected"),
    [
        (36, None, Decimal("1005.62")),
        (36, 36, Decimal("949.76")),
        (41, 36, Decimal("949.76")),
        (42, 36, Decimal("1005.62")),
        (47, 36, Decimal("1005.62")),
    ],
)
def test_prior_year_semesters_in_failed_title_extension(
    agreement: str, month: int, start: int | None, expected: Decimal
) -> None:
    """Work pay uses the previous year's semester only inside the extension."""
    ccnl = load_ccnl(agreement)
    apprentice = Apprentice(
        month,
        programme=ApprenticeshipProgramme.FIRST_LEVEL,
        track="qualifica_altri",
        hours=DualHours(Decimal(0), Decimal(0), Decimal(160)),
        failed_title_extension_start_month=start,
    )
    chain = dual_chain(
        ccnl,
        ccnl.level_by_code("1"),
        apprentice,
        0,
        frozenset(),
        date(2026, 6, 1),
        worker_category=None,
        seniority_months=None,
    )
    assert chain.base == expected
    assert "dual_apprenticeship_contributions" in chain.limitations
    assert "dual_apprenticeship_prorogation" not in chain.limitations


def test_extension_outside_first_level_or_after_a_year_is_refused() -> None:
    """The failed-title rule cannot pay a third-level or thirteenth month."""
    ccnl = load_ccnl("edilizia-ance")
    for month, programme, track, level in (
        (48, ApprenticeshipProgramme.FIRST_LEVEL, "qualifica_altri", "1"),
        (36, ApprenticeshipProgramme.THIRD_LEVEL, "alta_formazione_ricerca", "2"),
    ):
        with pytest.raises(OutOfScopeError):
            dual_chain(
                ccnl,
                ccnl.level_by_code(level),
                Apprentice(
                    month,
                    programme=programme,
                    track=track,
                    hours=DualHours(Decimal(0), Decimal(0), Decimal(160)),
                    failed_title_extension_start_month=36,
                ),
                0,
                frozenset(),
                date(2026, 6, 1),
                worker_category=None,
                seniority_months=None,
            )


@pytest.mark.parametrize("agreement", ["edilizia-ance", "edilizia-ance-impiegati"])
@pytest.mark.parametrize(
    ("track", "length", "start", "level"),
    [
        ("qualifica_altri", 36, 24, "1"),
        ("qualifica_altri", 24, 23, "1"),
        ("diploma_ifts", 48, 36, "2"),
        ("diploma_ifts", 12, 11, "2"),
    ],
)
def test_extension_cannot_begin_before_original_end(
    agreement: str, track: str, length: int, start: int, level: str
) -> None:
    """Before month 36 of a qualification, 85% is due, not the prior year's 75%."""
    ccnl = load_ccnl(agreement)
    with pytest.raises(InvalidInputError) as exc:
        dual_chain(
            ccnl,
            ccnl.level_by_code(level),
            Apprentice(
                start,
                programme=ApprenticeshipProgramme.FIRST_LEVEL,
                track=track,
                programme_months=length,
                hours=DualHours(Decimal(0), Decimal(0), Decimal(160)),
                failed_title_extension_start_month=start,
            ),
            0,
            frozenset(),
            date(2026, 6, 1),
            worker_category=None,
            seniority_months=None,
        )
    assert exc.value.field == "Apprentice.failed_title_extension_start_month"


def test_level_two_extension_needs_the_route_length() -> None:
    """The level-2 track holds the 12-month certificate and the 48-month diploma.

    Without ``programme_months`` the original end of the route is unknown,
    so the extension is refused with a missing fact, not guessed.
    """
    ccnl = load_ccnl("edilizia-ance")
    with pytest.raises(MissingRequiredFactError):
        dual_chain(
            ccnl,
            ccnl.level_by_code("2"),
            Apprentice(
                48,
                programme=ApprenticeshipProgramme.FIRST_LEVEL,
                track="diploma_ifts",
                hours=DualHours(Decimal(0), Decimal(0), Decimal(160)),
                failed_title_extension_start_month=48,
            ),
            0,
            frozenset(),
            date(2026, 6, 1),
            worker_category=None,
            seniority_months=None,
        )


def test_extension_start_must_be_positive() -> None:
    """A zero or negative contract month cannot begin an extension."""
    with pytest.raises(InvalidInputError):
        Apprentice(36, failed_title_extension_start_month=0)
